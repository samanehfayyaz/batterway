from pydantic import AnyUrl, BaseModel

from batterway.datamodel.generic.product import Quantity, Unit


### Battery parsers ###
class UnitPdt(BaseModel):
    """Pydantic parser model for the Unit class."""

    name: str
    iri: AnyUrl | None


class QuantityPdt(BaseModel):
    """Pydantic parser model for the Quantity class."""

    quantity: float | int
    unit: UnitPdt

    def to_quantity(self, unit_possible: dict[str, Unit]):
        return Quantity(self.quantity, unit_possible[self.unit.name])


class ProductPdt(BaseModel):
    """Pydantic parser model for the Product class."""

    name: str
    iri: AnyUrl | None
    reference_quantity: QuantityPdt
    BoM_id: str | None


class BoMPdt(BaseModel):
    """Pydantic parser model for the BoM class."""

    BoMId: str | None
    product_quantities: dict[str, QuantityPdt]


class ChemicalCompoundPdt(ProductPdt):
    """Pydantic parser model for the ChemicalCompound class."""

    chemical_formula: str
    reference_quantity: QuantityPdt


### RecyclingProcess parsers ###


class ProcessLCIPdt(BaseModel):
    """Pydantic parser model for the ProcessLCI class."""

    lci_id: str
    relative_lci_output: list[tuple[str, str, float]]
    relative_lci_input: list[tuple[str, str, float]]


class RecyclingProcess(BaseModel):
    """Pydantic parser model for the RecyclingProcess class."""

    name: str
    lci_input: ProcessLCIPdt
class RecyclingProcessPdt(BaseModel):
    process_name: str
    fixed_input_bom_id: str
    relative_lci: ProcessLCIPdt

class FixedLCIPdt(BaseModel):
    lci_id: str
    products: list[str]
    ref_in_rel_lci: str

