from pydantic import AnyUrl, BaseModel


from batterway.datamodel.generic.product import Quantity, Unit


### Battery parsers ###
class UnitPdt(BaseModel):
    name: str
    iri: AnyUrl | None


class QuantityPdt(BaseModel):
    quantity: float | int
    unit: UnitPdt

    def to_quantity(self, unit_possible: dict[str, Unit]):
        return Quantity(self.quantity, unit_possible[self.unit.name])


class ProductPdt(BaseModel):
    name: str
    iri: AnyUrl | None
    reference_quantity: QuantityPdt
    BoM_id: str | None


class BoMPdt(BaseModel):
    BoMId: str | None
    product_quantities: dict[str, QuantityPdt]


class ChemicalCompoundPdt(ProductPdt):
    chemical_formula: str
    reference_quantity: QuantityPdt


### RecyclingProcess parsers ###


class ProcessLCIFixed(BaseModel):
    lci_id: str
    product_quantities: dict[str, QuantityPdt]


class ProcessLCIRelative(BaseModel):
    lci_id: str
    reference_product: str
    product_quantities: dict[str, QuantityPdt]


class RecyclingProcess(BaseModel):
    name: str
    lci_input_fixed: ProcessLCIFixed
    lci_output_fixed: ProcessLCIFixed
    lci_input_relative: ProcessLCIRelative
    lci_output_relative: ProcessLCIRelative
