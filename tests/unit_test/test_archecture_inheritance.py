from batterway.datamodel.Generic.Product import Product, ProductArchetype, Quantity, ChemicalCompound


def test_architecture_inheritance():
    cathode = ChemicalCompound("NMC622", "", "LiNi0.6Mn0.2Co0.2O2")
    anode = ChemicalCompound("Graphite", "", "C")
    water = ChemicalCompound("Water", "", "H2O")
    cell_p = Product("CellNMC")
    module_p = Product("ModuleNMC")
    battery_p = Product("BatteryNMC")

    cell_nmc = ProductArchetype(
        cell_p,
        Quantity(1.0, "kg"),
        [
            (cathode,Quantity(0.33,"kg")),
            (anode,Quantity(0.33,"kg")),
            (water,Quantity(0.34,"kg"))
        ]
    )
    p_module_nmc = ProductArchetype(
        module_p,
        Quantity(1.0, "kg"),
        [
            (cell_p,Quantity(1.0,"kg"))
        ]
    )
    p_battery_nmc = ProductArchetype(
        battery_p,
        Quantity(1.0, "kg"),
        [
            (module_p, Quantity(1.0, "kg"))

        ]

    )

def test_final_bom():
    all_my_produyct= {}
    all_my_product_arch= {}
    all_my_product_isntance= {}
    def find_final_bom_of_instance(p_instance):
        pass