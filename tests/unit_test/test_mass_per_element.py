from batterway.datamodel.generic.process import Process
from batterway.datamodel.generic.product import ChemicalCompound, ProductInstance, Quantity


def test_mass_per_element_process_level():
    cathode = ChemicalCompound("NMC622", "", "LiNi0.6Mn0.2Co0.2O2")
    anode = ChemicalCompound("Graphite", "", "C")
    process = Process(
        "NMC622Cell",
        [
            ProductInstance(cathode, Quantity(1.6, "kg")),
            ProductInstance(anode, Quantity(1.6, "kg")),
        ],
        [],
    )
    process.get_output_total_mass_per_element()


test_mass_per_element_process_level()
