from pathlib import Path

from batterway.datamodel.parser.Inventory import Inventory


def test_parser() -> None:
    """Testing the inventory parser."""
    new_inventory = Inventory.create_from_file(Path(__file__).parent.parent.parent / "data/dataframes/")
    r_process = new_inventory.get_process("recycling_process_1")
    r_process.update_fixed_input_lci({"Battery_NMC442": 578.0})


test_parser()
