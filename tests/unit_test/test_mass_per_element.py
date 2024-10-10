from batterway.datamodel.generic.product import Process
from batterway.datamodel.generic.product import ChemicalCompound, Flow, Quantity


def test_mass_per_element_process_level():
    cathode = ChemicalCompound("NMC622","","LiNi0.6Mn0.2Co0.2O2")
    anode = ChemicalCompound("Graphite","","C")
    process = Process(
        "NMC622Cell",
        [
            Flow(cathode,Quantity(1.6,"kg")),
            Flow(anode,Quantity(1.6,"kg")),
        ],
        []
    )
    process.get_total_mass_per_element()
test_mass_per_element_process_level()
