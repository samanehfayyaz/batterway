from collections import Counter
from pathlib import Path

import pandas as pd

from batterway.datamodel.parser.parsers import UnitPdt, ProductPdt, ChemicalCompoundPdt, BoMPdt, QuantityPdt


class InventoryParser:
    def __init__(self):
        pass

    @classmethod
    def create_from_file(cls, file_name: Path):
        inventory = InventoryParser()
        pydt_units_obj = list(
            map(
                lambda x: UnitPdt(**x[1].to_dict()),
                InventoryParser.__read_csv(file_name.joinpath("units.csv")).iterrows()
            )
        )
        pydt_products_parsed = list(map(
            lambda x: ProductPdt(
                **x[1].to_dict()
                  |
                  {
                      "BoM":[],"Quantity":QuantityPdt(**{"quantity":x[1].to_dict()["reference_quantity"],"unit":pydt_units_obj[0]})
                  }
            ),
            InventoryParser.__read_csv(file_name.joinpath("products.csv")).fillna({"iri" : ""}).iterrows()
        ))
        print(pydt_products_parsed)
        pydt_chemical_compounds = list(map(
            lambda x: ChemicalCompoundPdt(**x[1].to_dict()),
            InventoryParser.__read_csv(file_name.joinpath("chemical_compounds.csv")).iterrows()
        ))
        all_products = {p.name: p for p in pydt_products_parsed+pydt_chemical_compounds}
        bom_per_product = dict()
        for product, df_bom_product in InventoryParser.__read_csv(file_name.joinpath("BoM.csv")).groupby("Product"):
            bom_per_product[product] = BoMPdt(
                product_quantities=[(all_products[row["Material"]], QuantityPdt(quantity=row["Quantity"], unit=pydt_units_obj[0]))
                 for _, row in df_bom_product.iterrows()]

            )

    @staticmethod
    def __read_csv(file_name: Path):
        return pd.read_csv(file_name, sep=";",decimal=".")
