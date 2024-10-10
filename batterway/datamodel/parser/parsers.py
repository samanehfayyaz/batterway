import pydantic

from batterway.datamodel.generic.product import Quantity, Unit


class UnitPdt(pydantic.BaseModel):
    name: str
    iri:str
class QuantityPdt(pydantic.BaseModel):
    quantity: float|int
    unit:UnitPdt

    def to_quantity(self,unit_possible:dict[str,Unit]):
        return Quantity(self.quantity, unit_possible[self.unit.name])

class ProductPdt(pydantic.BaseModel):
    name: str
    iri:str
    reference_quantity : QuantityPdt
    BoM_id: str|None

class BoMPdt(pydantic.BaseModel):
    BoMId: str|None
    product_quantities : dict[str, QuantityPdt]
class ChemicalCompoundPdt(ProductPdt):
    chemical_formula: str
    reference_quantity:QuantityPdt
class ProductInstance(pydantic.BaseModel):
    product: ProductPdt
    quantity:QuantityPdt
    BoM_id:BoMPdt
class Flow(pydantic.BaseModel):
    product: ProductPdt
    quantity:QuantityPdt
