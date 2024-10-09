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

    def __str__(self):
        return f"{self.value} {self.unit.name}"


class Product:
    def __init__(self, name: str, iri: str):
        self.name = name
        self.iri = ProductIRI(iri)
    
    def __str__(self):
        return self.name


class BoM:
    def __init__(self, product_quantities: dict[Product, Quantity]):
        self.product_quantities: dict[Product, Quantity] = product_quantities
        self.products = product_quantities.keys()
        self.quantity_total = sum(product_quantities.values())

    def __str__(self) -> str:
        return "\n".join([f"{p.name}: {q}" for p, q in self.product_quantities.items()])


class ProductArchetype:
    def __init__(self, product: Product, reference_quantity: Quantity, bom: dict[Product, Quantity] | None):
        self.product: Product = product
        self.reference_quantity: Quantity = reference_quantity
        self.bom: BoM = bom

        # Check that the sum of quantities in the BoM is equal to the reference quantity
        if bom is not None:
            if bom.quantity_total != reference_quantity:
                raise ValueError("The sum of quantities in the BoM is not equal to the reference quantity")
        
        def __str__(self):
            return f"{self.reference_quantity} of {self.product.name}"


class ProductInstance:
    def __init__(self, product_archteype: ProductArchetype, quantity: Quantity):
        self.product_archetype: ProductArchetype = product_archteype
        self.qty: Quantity = quantity
        self.bom: BoM = BoM({p: qty * self.qty for p, qty in self.product_archetype.bom.product_quantities.items()})
    
    def __str__(self):
        return f"{self.qty} of {self.product_archetype.product.name}"


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
