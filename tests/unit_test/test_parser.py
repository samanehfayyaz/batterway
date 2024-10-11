from pathlib import Path

from batterway.datamodel.parser.Inventory import Inventory


def test_parser():
    new_inventory = Inventory.create_from_file(Path("C:/Users/the-m/PycharmProjects/batterway/data/dataframes/"))
    new_inventory.process_inventory()
    r_process = new_inventory.get_process("route1")
    r_process.set_influencing_output_process()
    r_process.set()

test_parser()
