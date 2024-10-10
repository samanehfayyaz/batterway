from codecs import BOM
from batterway.datamodel.generic.product import Product, ProductArchetype, Quantity



class Celltype(Enum):
    NMC622  = "NMC622"
    NMC811: str = "NMC811"
    LFP: str = "LFP"




class EletrochemicalCell:
    def __init__(self, product_archetype: ProductArchetype):
        self.product_archetype = product_archetype
        self.cell_type = product_archetype.product.name
        self.unique_id = uuid

