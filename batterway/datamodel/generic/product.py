"""generic data model classes for products, quantities, and bills of materials."""

from collections import Counter

from chempy import Substance
from chempy.util.periodic import relative_atomic_masses, symbols
from rdflib import URIRef
from sentier_data_tools.iri import ProductIRI, UnitIRI


class Unit:
    """A unit of measurement with sentier.dev URI."""

    def __init__(self, name: str, iri: str):
        self.name = name
        self.iri = UnitIRI(iri)


class Quantity:
    """A quantity with a unit of measurement."""

    def __init__(self, value: float, unit: Unit):
        self.value: float = value
        self.unit: Unit = unit

    def _compatibility_check(self, other: "Quantity | float | int") -> bool:
        """Check if an object is compatible with the Quantity object."""
        if isinstance(other, Quantity):
            if other.unit != self.unit:
                err_msg = f"Units {self.unit.name} and {other.unit.name} are not compatible"
                raise ValueError(err_msg)
        elif not isinstance(other, float | int):
            err_msg = (
                f"Quantity is not compatible with {other.__class__.__name__}, only with float, int or Quantity objects."
            )
            return TypeError(err_msg)
        return True

    def __eq__(self, other: "Quantity") -> bool:
        if isinstance(other, Quantity):
            return self.value == other.value and self.unit == other.unit
        if isinstance(other, int|float):
            return self.value == other
        return False

    def __add__(self, other: "Quantity | float | int") -> "Quantity":
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return Quantity(self.value + other.value, self.unit)
            if isinstance(other, float | int):
                return Quantity(self.value + other, self.unit)
        return None

    def __radd__(self, other: "Quantity | float | int") -> "Quantity":
        if self._compatibility_check(other) and (other == 0 or (isinstance(other, Quantity) and other.value == 0)):
            return self
        return self.__add__(other)

    def __sub__(self, other: "Quantity | float | int") -> "Quantity":
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return Quantity(self.value - other.value, self.unit)
            if isinstance(other, float | int):
                return Quantity(self.value - other, self.unit)
        return None

    def __mul__(self, other: "Quantity | float | int") -> "Quantity":
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return Quantity(self.value * other.value, self.unit)
            if isinstance(other, float | int):
                return Quantity(self.value * other, self.unit)
        return None

    def __gt__(self, other: "Quantity | float | int") -> bool:
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return self.value > other.value
            if isinstance(other, float | int):
                return self.value > other
        return None

    def __str__(self) -> str:
        return f"{round(self.value, 5)} {self.unit.name}"


class Product:
    """A product with a name, sentier.dev ProductIRI, reference quantity and a BoM."""

    def __init__(self, name: str, iri: str, reference_quantity: Quantity, bom: "BoM | None" = None):
        self.name: str = name
        self.iri: ProductIRI = ProductIRI(iri)
        self.reference_quantity: Quantity = reference_quantity
        self.bom: BoM = bom

        # Check that the sum of quantities in the BoM is equal to the reference quantity
        if bom is not None and self.bom.quantity_total != reference_quantity:
            err_msg = f"Sum of quantities in BoM ({self.bom.quantity_total}) is not equal to reference quantity ({reference_quantity})"
            raise ValueError(err_msg)

    def __str__(self):
        bom_str = str(self.bom) if self.bom else ""
        return f"{self.name}[Ref:{self.reference_quantity}] " + bom_str

    def get_final_bom(self) -> "BoM":
        final_bom = BoM({self: ProductInstance(self,self.reference_quantity)})
        if self.bom:
            final_bom = BoM({})
            for product, p_instance in self.bom.product_quantities.items():
                if product.bom is None:  # Within the model, this means the product is a raw material
                    final_bom += BoM({product: p_instance})
                else:
                    final_bom += product.get_final_bom() * p_instance.qty
        return final_bom


class BoM:
    """A Bill of Materials with a dictionary of products and quantities."""

    def __init__(self, product_quantities: dict[Product,'ProductInstance']):
        self.product_quantities: dict[Product,'ProductInstance'] = product_quantities
        self.products = [p.product for p in product_quantities.values()]
        self.quantity_total = sum(x.qty.value for x in product_quantities.values())

    def __str__(self) -> str:
        return "\n".join([f"{p.name}: {q}" for p, q in self.product_quantities.items()])

    def __add__(self, other: "BoM") -> "BoM":
        """Add two BoM objects together and return a new BoM."""
        if not isinstance(other, BoM):
            err_msg = f"Can only add BoM objects together, not {other.__class__.__name__}"
            raise TypeError(err_msg)
            return None

        combined_quantities = dict(Counter(self.product_quantities) + Counter(other.product_quantities))
        return BoM(combined_quantities)

    def __mul__(self, other: "Quantity | float | int") -> "BoM":
        """Multiply a BoM by a Quantity object and return a new BoM."""
        if not isinstance(other, Quantity | float | int):
            err_msg = (
                f"Can only multiply BoM objects with int, float, or Quantity objects, not {other.__class__.__name__}"
            )
            raise TypeError(err_msg)
            return None

        multiplied_quantities = {p: q * other for p, q in self.product_quantities.items()}
        return BoM(multiplied_quantities)

    def __contains__(self, item):
        if isinstance(item, str):
            return item in [p.name for p in self.products]
        elif isinstance(item, ProductInstance):
            return item.product in self.products
        elif isinstance(item, Product):
            return item in self.products


class ProductInstance:
    """An instance of a product with a specific quantity."""

    def __init__(self, product: Product, quantity: Quantity):
        self.product: Product = product
        self.qty: Quantity = quantity
        self.bom: BoM = BoM(
            {p: qty * self.qty for p, qty in self.product.bom.product_quantities.items()}) if self.product.bom else {}

    def get_final_bom(self) -> BoM:
        return self.product.get_final_bom() * self.qty

    def _compatibility_check(self, other: "ProductInstance | Quantity | float | int") -> bool:
        """Check if an object is compatible with the Quantity object."""
        if isinstance(other, ProductInstance):
            if other.product != self.product:
                err_msg = f"Units {self.product.name} and {other.product.name} are not compatible"
                raise ValueError(err_msg)
        elif not isinstance(other, float | int | Quantity):
            err_msg = (
                f"Quantity is not compatible with {other.__class__.__name__}, only with float, int or Quantity objects."
            )
            return TypeError(err_msg)
        return True

    def __eq__(self, other: "ProductInstance") -> bool:
        if isinstance(other, Quantity):
            return self.qty == other.qty and self.product == other.product
        return False

    def __add__(self, other: "ProductInstance | Quantity | float | int") -> "ProductInstance":
        if self._compatibility_check(other):
            if isinstance(other, ProductInstance):
                return ProductInstance(self.product, self.qty + other.qty)
            if isinstance(other, Quantity):
                return ProductInstance(self.product, self.qty + other.value)
            if isinstance(other, float | int):
                return ProductInstance(self.product, self.qty + other)
        return None

    def __radd__(self, other: "ProductInstance | Quantity | float | int") -> "ProductInstance":
        if (self._compatibility_check(other)
                and (
                        other == 0 or (isinstance(other, Quantity) and other.value == 0)
                        or
                        (isinstance(other, ProductInstance) and other.qty == 0)
                )
        ):
            return self
        return self.__add__(other)

    def __sub__(self, other: "ProductInstance | Quantity | float | int") -> "ProductInstance":
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return ProductInstance(self.product, self.qty - other.value)
            if isinstance(other, ProductInstance):
                return ProductInstance(self.product, self.qty - other.qty)
            if isinstance(other, float | int):
                return ProductInstance(self.product, self.qty - other)
        return None

    def __mul__(self, other: "ProductInstance | Quantity | float | int") -> "ProductInstance":
        if self._compatibility_check(other):
            if isinstance(other, ProductInstance):
                return ProductInstance(self.product, self.qty * other.qty)
            if isinstance(other, Quantity):
                return ProductInstance(self.product, self.qty * other.value)
            if isinstance(other, float | int):
                return ProductInstance(self.product, self.qty * other)
        return None

    def __gt__(self, other: "ProductInstance | Quantity | float | int") -> bool:
        if self._compatibility_check(other):
            if isinstance(other, Quantity):
                return self.qty > other
            if isinstance(other, float | int):
                return self.qty > other
            if isinstance(other, ProductInstance):
                return self.qty > other.qty
        return None

    def __str__(self):
        return f"{self.qty} of {self.product.name}"


class ChemicalCompound(Product):
    """A chemical compound with a name, sentier.dev ProductIRI, and chemical formula."""

    def __init__(self, name: str, iri: URIRef, reference_quantity: Quantity, formula: str):
        super().__init__(name, iri, reference_quantity, bom=None)
        self.__chemical_formula: Substance = Substance.from_formula(formula)
        self.molar_mass = self.__chemical_formula.mass

    def _get_mass_per_element(self) -> dict[str, float]:
        """Get the atomic mass of each element in the chemical formula."""
        return {
            symbols[ele - 1]: (relative_atomic_masses[ele - 1] * qty)
            for ele, qty in self.__chemical_formula.composition.items()
        }

    def get_molar_share(self) -> dict[str, float]:
        """Get the relative mass of each element in the chemical formula."""
        mass_per_element = self._get_mass_per_element()
        total_mass = sum(mass_per_element.values())
        return {elem: mass / total_mass for elem, mass in mass_per_element.items()}
