from batterway.datamodel.Generic.Product import Product


class Flow:
    def __init__(self, product:Product, quantity, provider):
        self.product:Product = product
        self.quantity = quantity
        self.provider = provider
