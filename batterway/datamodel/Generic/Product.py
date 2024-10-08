from typing import Tuple, List

import chempy
from sentier_data_tools.iri import ProductIRI, UnitIRI
from chempy import Substance
from chempy.util.periodic import atomic_number, mass_from_composition, relative_atomic_masses, _elements

atom
class Unit:
    def __init__(self, name, iri: str):
        self.name = name
        self.dimensionality = ""
        self.unit = UnitIRI(iri)


class Quantity:
    def __init__(self, value, unit: Unit):
        self.value: float = value
        self.unit: Unit = unit


class Product:

    def __init__(self, name, IRI):
        self.name = name
        self.IRI: ProductIRI = IRI

class ChemicalCompound(Product):
    def __init__(self,name,IRI, formulae):
        super().__init__(name, IRI)
        self.__density = ""
        self.__molar_mass = ""
        self.__chemical_formulae:chempy.Substance = Substance.from_formula(formulae)

    def get_molar_share(self):
        mass_per_elemen = self.get_mass_per_element()
        total_mass = sum(mass_per_elemen.values())
        return {elem: mass / total_mass for elem, mass in mass_per_elemen.items()}

    def get_mass_per_element(self):
        return {
            _elements[ele-1]:(_elements[ele-1][2] * qty)
            for ele, qty in self.__chemical_formulae.composition.items()
        }


class Flow:
    def __init__(self, product: Product, quantity):
        self.product: Product = product
        self.quantity: Quantity = quantity

