from batterway.datamodel.generic.product import Product, Quantity, Unit

# Define the Unit for kg
kg = Unit("kg", "kg_IRI")
kWh = Unit("kWh", "kWh_IRI")
ratio = Unit("ratio", "ratio_iri")

# Define raw materials as Products
nickel = Product("nickel", "nickel.com", Quantity(1.0, kg))
manganese = Product("manganese", "manganese.com", Quantity(1.0, kg))
cobalt = Product("cobalt", "cobalt.com", Quantity(1.0, kg))
steel = Product("steel", "steel.com", Quantity(1.0, kg))
water = Product("water", "water.com", Quantity(1.0, kg))
heat = Product("heat", "heat.com", Quantity(1.0, kg))
vapor = Product("vapor", "vapor.com", Quantity(1.0, kg))