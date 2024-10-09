from typing import List

from batterway.datamodel.generic.Product import Product, ProductArchetype, ProductInstance


class WorldBank:
    def __init__(self, products: list[Product], product_archetypes: list[ProductArchetype], product_instances: list[ProductInstance]):
        self.products: dict[str, Product] = {Product.name: Product for Product in products}
        self.product_archetypes: dict[str, ProductArchetype] = {ProductArchetype.product.name: ProductArchetype for ProductArchetype in product_archetypes}
        self.product_instances: dict[str, ProductInstance] = {ProductInstance.product_archetype.product.name: ProductInstance for ProductArchetype in product_archetypes}

    def get_product_instance_leaves(self, product_instance: ProductInstance):
        for product in product_instance.bom:
            if product in self.product_archetypes:
                product_archetype_bom = self.product_archetypes[product][0].bom
                product_queue.append(product_archetype_bom)



    
