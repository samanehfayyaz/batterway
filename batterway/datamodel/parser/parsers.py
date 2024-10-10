import pydantic

class UnitPdt(pydantic.BaseModel):
    name: str
    iri:str
class QuantityPdt(pydantic.BaseModel):
    quantity: float
    unit:UnitPdt

class ProductPdt(pydantic.BaseModel):
    name: str
    iri:str
    reference_quantity : QuantityPdt
    BoM_id: str

class BoMPdt(pydantic.BaseModel):
    product_quantities : dict[str, QuantityPdt]
class ChemicalCompoundPdt(ProductPdt):
    chemical_formulae: str
    reference_quantity:QuantityPdt
class ProductInstance(pydantic.BaseModel):
    product: ProductPdt
    quantity:QuantityPdt
    BoM_id:BoMPdt
class Flow(pydantic.BaseModel):
    product: ProductPdt
    quantity:QuantityPdt
