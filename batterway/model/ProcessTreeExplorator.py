from typing import List

from batterway.datamodel.generic.Process import Process
from batterway.datamodel.generic.Product import Product, ProductArchetype, ProductInstance


class ProcessTreeExplorator:
    def __init__(self, process: Process):
        self.processes = process
        self.products: dict[str, Product] = dict()
        self.product_archetypes: dict[str, List[ProductArchetype]] = dict()
        self.product_instances: dict[str, ProductInstance] = dict()

    def build_leaf_inventory(self, product_instance: ProductInstance):
        product_queue = [product_instance.get_absolute_bom()]
        for product in product_instance.product_archtype.bom:
            if product in self.product_archetypes:
                product_archetype_bom = self.product_archetypes[product][0].bom
                product_queue.append(product_archetype_bom)


def build_leaf_inventory(product_instance: ProductInstance):
    
    product_instance.get_absolute_bom()
    
