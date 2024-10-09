from collections import Counter
from typing import Optional

from chempy import Substance
from chempy.util.periodic import relative_atomic_masses, symbols
from scipy.fftpack import ifft2
from sentier_data_tools.iri import ProductIRI, UnitIRI
from sympy import false


class Unit:
    def __init__(self, name, iri: str):
        self.name = name
        self.iri = UnitIRI(iri)


class Quantity:
    def __init__(self, value, unit: Unit):
        self.value: float = value
        self.unit: Unit = unit

    def __check_compat_operation(self, other):
        if isinstance(other, Quantity):
            if other.unit != self.unit:
                raise ValueError("Quantity have to be of the same unit")
        elif not isinstance(other, float | int):
            raise ValueError("Quantity has to be a float, int or Quantity object")

    def __eq__(self, other):
        if isinstance(other, Quantity):
            return self.value == other.value and self.unit == other.unit
        return False

    def __add__(self, other):
        self.__check_compat_operation(other)
        if isinstance(other, Quantity):
            return Quantity(self.value + other.value, self.unit)
        if isinstance(other, float | int):
            return Quantity(self.value + other, self.unit)

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __sub__(self, other):
        self.__check_compat_operation(other)
        if isinstance(other, Quantity):
            return Quantity(self.value - other.value, self.unit)
        if isinstance(other, float | int):
            return Quantity(self.value - other, self.unit)

    def __mul__(self, other):
        self.__check_compat_operation(other)
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit)
        if isinstance(other, float | int):
            return Quantity(self.value * other, self.unit)

    def __gt__(self, other):
        self.__check_compat_operation(other)
        if isinstance(other, Quantity):
            return self.value > other.value
        if isinstance(other, float | int):
            return self.value > other

    def __str__(self):
        return f"{round(self.value, 5)} {self.unit.name}"


class Product:
    def __init__(self, name: str, iri: str, reference_quantity: Quantity, bom: Optional["BoM"] = None):
        self.name: str = name
        self.iri: ProductIRI = ProductIRI(iri)
        self.reference_quantity: Quantity = reference_quantity
        self.bom: BoM = bom

        # Check that the sum of quantities in the BoM is equal to the reference quantity
        if bom is not None and self.bom.quantity_total != reference_quantity:
            raise ValueError("The sum of quantities in the BoM is not equal to the reference quantity")

    def __str__(self):
        return f"{self.reference_quantity} of {self.name}"

    def get_final_bom(self) -> "BoM":
        if self.bom is None:
            return None
        final_bom = BoM({})
        for product, qty in self.bom.product_quantities.items():
            if product.bom is None:  # Within the model, this means the product is a raw material
                final_bom += BoM({product: qty})
            else:
                final_bom += product.get_final_bom() * qty
        return final_bom


class BoM:
    def __init__(self, product_quantities: dict[Product, Quantity]):
        self.product_quantities = product_quantities
        self.products = product_quantities.keys()
        self.quantity_total = sum(product_quantities.values())

    def __str__(self) -> str:
        return "\n".join([f"{p.name}: {q}" for p, q in self.product_quantities.items()])

    def __add__(self, other):
        """Add two BoM objects together and return a new BoM."""
        if not isinstance(other, BoM):
            return TypeError("Can only add BoM objects together")

        combined_quantities = dict(Counter(self.product_quantities) + Counter(other.product_quantities))
        return BoM(combined_quantities)

    def __mul__(self, other):
        """Multiply a BoM by a Quantity object and return a new BoM."""
        if not isinstance(other, Quantity | float | int):
            return TypeError("Can only multiply BoM objects by Quantity objects")

        multiplied_quantities = {p: q * other for p, q in self.product_quantities.items()}
        return BoM(multiplied_quantities)


class ProductInstance:
    def __init__(self, product: Product, quantity: Quantity):
        self.product: Product = product
        self.qty: Quantity = quantity
        self.bom: BoM = BoM({p: qty * self.qty for p, qty in self.product.bom.product_quantities.items()})

    def get_final_bom(self) -> BoM:
        return self.product.get_final_bom() * self.qty

    def __str__(self):
        return f"{self.qty} of {self.product.name}"


class ChemicalCompound(Product):
    def __init__(self, name, iri, formulae):
        super().__init__(name, iri)
        self.__chemical_formulae: Substance = Substance.from_formula(formulae)
        self.molar_mass = self.__chemical_formulae.mass

    def _get_mass_per_element(self):
        return {
            symbols[ele - 1]: (relative_atomic_masses[ele - 1] * qty)
            for ele, qty in self.__chemical_formulae.composition.items()
        }

    def get_molar_share(self):
        mass_per_elemen = self._get_mass_per_element()
        total_mass = sum(mass_per_elemen.values())
        return {elem: mass / total_mass for elem, mass in mass_per_elemen.items()}


class Flow:
    """Directional and quantified flow of a product."""

    def __init__(self, product: Product, quantity: Quantity):
        self.product: Product = product
        self.quantity: Quantity = quantity

    def __is_op_compact(self, other):
        if isinstance(other, Flow):
            if other.product != self.product:
                raise ValueError("Flow have to be of the same product")
        elif not isinstance(other, float | int):
            raise ValueError("Flow can be update only with float|int")

    def __add__(self, other):
        self.__is_op_compact(other)
        if isinstance(other, Flow):
            return Flow(self.product, self.quantity + other.quantity)
        return Flow(self.product, self.quantity + other)

    def __mult__(self, other):
        self.__is_op_compact(other)
        if isinstance(other, Flow):
            return Flow(self.product, self.quantity * other.quantity)
        return Flow(self.product, self.quantity * other)
