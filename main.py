from pathlib import Path

from batterway.datamodel.parser.Inventory import Inventory

if __name__ == '__main__':
    new_inventory = Inventory.create_from_file(Path(__file__).parent / "data/dataframes/")
    r_process = new_inventory.get_process("recycling_process_1")
    r_process.update_fixed_input_lci({"Battery_NMC442": 578.0})
