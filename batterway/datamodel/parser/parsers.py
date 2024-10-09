import pydantic

class UnitPdt(pydantic.BaseModel):
    name: str
    iri:str
class Quantity(pydantic.BaseModel):
    quantity: float
    unit:UnitPdt

class ProductPdt(pydantic.BaseModel):
    name: str
    iri:str
    values: list[tuple[ProductPdt,Quantity]]

class ChemicalCompoundPdt(ProductPdt):
    chemical_formulae: str

class ProductArchetype(pydantic.BaseModel):
    name: str
    reference_quantity:Quantity
    bom:BoMPdt

class ProductInstance(pydantic.BaseModel):
    name: str
    quantity:Quantity
    archetype:ProductArchetype

class Flow(pydantic.BaseModel):
    product: ProductPdt
    quantity:Quantity
