from chempy import Substance
from chempy.util.periodic import relative_atomic_masses, symbols
from Process import Process
from sentier_data_tools.iri import ProductIRI, UnitIRI


class Unit:
    def __init__(self, name, iri: str):
        self.name = name
        self.iri = UnitIRI(iri)


class Quantity:
    def __init__(self, value, unit: Unit):
        self.value: float = value
        self.unit: Unit = unit

    def __add__(self, other):
        self.__check_compat_operation(other)
        if other.unit != self.unit:
            raise ValueError("Quantity have to be of the same unit")
        if isinstance(other, Quantity):
            if other.unit == self.unit:
                return Quantity(self.value + other.value, self.unit)
            else:
                raise ValueError("Quantity have to be of the same unit")
        elif isinstance(other,float|int):
            return Quantity(self.value + other, self.unit)
    def __check_compat_operation(self,other):
        if isinstance(other, Quantity):
            if other.unit != self.unit:
                raise ValueError("Quantity have to be of the same unit")
        elif not isinstance(other,float|int):
            raise ValueError("Quantity have to be of the same unit")
    def __mult__(self, other):
        self.__check_compat_operation(other)
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit)
        elif isinstance(other,float|int):
            return Quantity(self.value * other, self.unit)

class Product:
    def __init__(self, name, iri):
        self.name = name
        self.iri: ProductIRI = iri


class ProductArchetype:
    def __init__(self, product: Product, reference_quantity: Quantity, bom: dict[Product, Quantity] | None):
        self.product: Product = product
        self.reference_quantity: Quantity = reference_quantity
        self.bom: dict[Product, Quantity] | None = bom


class ProductInstance:
    def __init__(self, product_archteype: ProductArchetype, quantity: Quantity):
        self.product_archtype: ProductArchetype = product_archteype
        self.qty: Quantity = quantity

    def get_absolute_bom(self):
        return {p: qty*self.qty for p, qty in self.product_archtype.bom.items()}


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

    def __init__(self, product: Product, quantity: Quantity, source_process: Process, target_process: Process):
        self.product: Product = product
        self.quantity: Quantity = quantity
        self.source_process: Process = None
        self.target_process: Process = None
