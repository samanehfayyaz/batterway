from pathlib import Path

from batterway.datamodel.parser.Inventory import Inventory


def test_parser():
    Inventory.create_from_file(Path("C:/Users/the-m/PycharmProjects/batterway/data/dataframes/"))


test_parser()
