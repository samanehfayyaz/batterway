from batterway.datamodel.generic.product import Product, Quantity, Unit, BoM, ProductInstance

# Define the Unit for kg
kg = Unit("kg", "kg_IRI")
kWh = Unit("kWh", "kWh_IRI")

# Define raw materials as Products
nickel = Product("nickel", "nickel.com", Quantity(1.0, kg))
manganese = Product("manganese", "manganese.com", Quantity(1.0, kg))
cobalt = Product("cobalt", "cobalt.com", Quantity(1.0, kg))
nmc111 = Product(
    "nmc111", "nmc111.com", Quantity(1.0, kg),
    bom=BoM(
        {
            nickel: ProductInstance(nickel, Quantity(0.3, kg)),
            manganese: ProductInstance(manganese, Quantity(0.4, kg)),
            cobalt: ProductInstance(cobalt, Quantity(0.3, kg))
        }
    )
)
steel = Product("steel", "steel.com", Quantity(1.0, kg))
water = Product("water", "water.com", Quantity(1.0, kg))
heat = Product("heat", "heat.com", Quantity(1.0, kg))
vapor = Product("vapor", "vapor.com", Quantity(1.0, kg))

# Define raw materials as Products
chocolate = Product("nickel", "nickel.com", Quantity(1.0, kg))
wheat = Product("wheat", "wheat.com", Quantity(1.0, kg))
black_wheat = Product("black_wheat", "black_wheat.com", Quantity(1.0, kg))

flour = Product(
    "flour", "flour.com", Quantity(1.0, kg),
    bom=BoM(
        {
            wheat: ProductInstance(wheat, Quantity(0.5, kg)),
            black_wheat: ProductInstance(black_wheat, Quantity(0.5, kg)),
        }
    )
)
doe = Product("doe", "brownie.com", Quantity(1.0, kg),
              bom=BoM(
                  {
                      water: ProductInstance(water, Quantity(0.5, kg)),
                      flour: ProductInstance(water, Quantity(0.5, kg)),
                  }
              )
              )

schwarze_kuchen = Product(
    "schwarze_kuchen", "schwarze_kuchen.com",
    Quantity(1.0, kg),
    bom=BoM(
        {
            chocolate: Quantity(0.7, kg),
            doe: Quantity(0.3, kg),
        }
    ),
)
cookie = Product(
    "cookie", "cookie.com",
    Quantity(1.0, kg),
    bom=BoM(
        {
            chocolate: Quantity(0.3, kg),
            doe: Quantity(0.7, kg),
        }
    )
)
brownie = Product(
    "brownie", "brownie.com",
    Quantity(1.0, kg), bom=BoM(
        {
            chocolate: Quantity(0.5, kg),
            doe: Quantity(0.5, kg),
        }
    )
)
