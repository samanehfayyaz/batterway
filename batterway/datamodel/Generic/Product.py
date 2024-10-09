from chempy import Substance
from chempy.util.periodic import relative_atomic_masses, symbols
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
        if isinstance(other, Quantity):
            if other.unit == self.unit:
                return Quantity(self.value + other.value, self.unit)
            else:
                raise ValueError("Quantity have to be of the same unit")
        elif isinstance(other,float|int):
            return Quantity(self.value + other, self.unit)


class Product:
    def __init__(self, name, iri):
        self.name = name
        self.iri: ProductIRI = iri


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
    def __init__(self, product: Product, quantity: Quantity):
        self.product: Product = product
        self.quantity: Quantity = quantity
        # todo fix with real stuff
        # assert self.quantity.unit == "mass"

    def get_total_mass_per_element(self):
        if isinstance(self.product, ChemicalCompound):
            return {element:Quantity(share*self.quantity.value,self.quantity.unit)
                    for element,share in self.product.get_molar_share().items()}
        else:
            raise NotImplementedError("Only implemented for chemical compound type")
