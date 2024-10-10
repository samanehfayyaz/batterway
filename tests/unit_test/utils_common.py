from batterway.datamodel.generic.product import Product, Quantity, Unit

# Define the Unit for kg
kg = Unit("kg", "kg_IRI")

# Define raw materials as Products
nickel = Product("nickel", "nickel.com", Quantity(1.0, kg))
manganese = Product("manganese", "manganese.com", Quantity(1.0, kg))
cobalt = Product("cobalt", "cobalt.com", Quantity(1.0, kg))
steel = Product("steel", "steel.com", Quantity(1.0, kg))