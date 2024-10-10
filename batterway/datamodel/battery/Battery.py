from batterway.datamodel.generic.product import Product, Quantity

class Celltype(Enum):
    NMC622  = "NMC622"
    NMC811: str = "NMC811"
    LFP: str = "LFP"

class EletrochemicalCell:
    def __init__(self, product: Product):
        self.product = product
        self.cell_type = product.name
class Battery:
    def __init__(self, battery_level):
        pass
