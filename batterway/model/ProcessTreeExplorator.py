from typing import List

from batterway.datamodel.Generic.Process import Process
from batterway.datamodel.Generic.Product import ProductInstance, ProductArchetype, Product


class ProcessTreeExplorator:
    def __init__(self, process:Process):
        self.processes = process
        self.products:dict[str,Product] = dict()
        self.product_archetypes:dict[str,List[ProductArchetype]] = dict()
        self.product_instances:dict[str,ProductInstance] = dict()

    def __get_archetypes(self,product:str):

    def build_leaf_inventory(self,product_instance:ProductInstance):
        material_component = {}
        product_queue= [product_instance.get_absolute_bom()]
        for product in product_instance.product_archtype.bom:
            if product in self.product_archetypes:
                product_archetype_bom = self.product_archetypes[product][0].bom
                product_queue.append(product_archetype_bom)
        pass


