from typing import Dict, List, Tuple

from pydantic import BaseModel

from batterway.datamodel.Generic.LUCA import LUCA
from batterway.datamodel.Generic.Quantity import Quantity

class dataProduct(BaseModel):
    name:str
    IRI:str
    def __init__(self,name:str,IRI:str):

        self.name = name
        self.IRI = IRI




class Product(LUCA):

    def __init__(self, name,IRI, description, composition, uid, metadata: Dict[str, str]):
        super().__init__(uid, metadata)
        self.name = name
        self.IRI = IRI
        self.description = description
        self.composition:List[Tuple['Product',Quantity]] = composition


    @classmethod
    def class_builder(cls, dataProduct:dataProduct) -> 'Product':
        return cls(dataProduct.name,)