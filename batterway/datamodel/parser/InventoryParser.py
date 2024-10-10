from collections import Counter
from pathlib import Path

import pandas as pd

from batterway.datamodel.generic.product import Product, Unit, ProductInstance, Quantity, BoM, ChemicalCompound
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
        all_unit = {u.name: u for u in pydt_units_obj}
        # Prse product
        pydt_products_parsed = list(map(
            lambda x: ProductPdt(
                **x[1].to_dict()
                  |
                  {
                      "reference_quantity": QuantityPdt(**{"quantity": x[1].to_dict()["reference_quantity"],
                                                           "unit": all_unit[x[1].to_dict()["unit"]]})
                  }
            ),
            InventoryParser.__read_csv(file_name.joinpath("products.csv")).fillna({"iri": "", "BoM_id": ""}).iterrows()
        ))
        # Parse chemical
        pydt_chemical_compounds = list(map(
            lambda x: ChemicalCompoundPdt(
                **x[1].to_dict()
                  |
                  {
                      "reference_quantity": QuantityPdt(**{"quantity": x[1].to_dict()["reference_quantity"],
                                                           "unit": all_unit[x[1].to_dict()["unit"]]})
                  }
            ),
            InventoryParser.__read_csv(file_name.joinpath("chemical_compounds.csv")).fillna(
                {"iri": "", "BoM_id": ""}).iterrows()
        ))
        # Merge chemical and product as they should be unique by Id
        all_products = {p.name: p for p in pydt_products_parsed + pydt_chemical_compounds}
        all_boms = dict()
        for BoMId, df_bom_product in InventoryParser.__read_csv(file_name.joinpath("BoM.csv")).groupby("BoMId"):
            all_boms[BoMId] = BoMPdt(
                **{
                    "BoMId": BoMId,
                    "product_quantities": {
                        all_products[row["Material"]].name:
                            QuantityPdt(quantity=row["Quantity"], unit=all_unit[row['Unit']])
                        for _, row in df_bom_product.iterrows()
                    }
                }

            )
        # Now we have to create the real object
        # And associate the BoM to their respective product
        real_units = {u.name : u for u in map(lambda x: Unit(x[1].name, x[1].iri), all_unit.items())}
        real_products = map(
            lambda x:
            Product(x[1].name, x[1].iri,x[1].reference_quantity.to_quantity(real_units),bom=None) if isinstance(x[1],ProductPdt) else
            ChemicalCompound(x[1].name, x[1].iri,x[1].reference_quantity.to_quantity(real_units),bom=None)
            ,
            all_products.items()
        )
        real_product_dict = {p.name: p for p in real_products}
        real_BoM = dict(map(lambda v : (v[1].BoMId,BoM({real_product_dict[p]:p_qty.to_quantity(real_units)
            for p,p_qty in v[1].product_quantities.items()
        })),all_boms.items()))

        for p in all_products:
            if all_products[p].BoM_id:
                real_product_dict[p].bom = real_BoM[all_products[p].BoM_id]

        for p in real_product_dict.values():
            print(p)
    @staticmethod
    def __read_csv(file_name: Path):
        return pd.read_csv(file_name, sep=";", decimal=".")
