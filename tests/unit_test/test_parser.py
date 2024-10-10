from pathlib import Path

from batterway.datamodel.parser.Inventory import InventoryParser


def test_parser():
    InventoryParser.create_from_file(
        Path("C:/Users/the-m/PycharmProjects/batterway/data/data_for_test/")
    )

test_parser()