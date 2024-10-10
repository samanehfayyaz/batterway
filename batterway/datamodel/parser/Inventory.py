from pathlib import Path

import pandas as pd

from batterway.datamodel.generic.product import BoM, ChemicalCompound, Product, Unit
from batterway.datamodel.parser.parsers import BoMPdt, ChemicalCompoundPdt, ProductPdt, QuantityPdt, UnitPdt


class Inventory:
    def __init__(self, units: dict[str, Unit] | None, products: list[str:Product] | None):
        self.units = units
        self.products = products

    @classmethod
    def create_from_file(cls, file_name: Path):
        pydt_units_obj = [
            UnitPdt(**x[1].to_dict()) for x in Inventory.__read_csv(file_name.joinpath("units.csv")).iterrows()
        ]
        all_unit = {u.name: u for u in pydt_units_obj}
        # Parse product
        pydt_products_parsed = [
            ProductPdt(
                **x[1].to_dict()
                | {
                    "reference_quantity": QuantityPdt(
                        quantity=x[1].to_dict()["reference_quantity"], unit=all_unit[x[1].to_dict()["unit"]]
                    )
                }
            )
            for x in Inventory.__read_csv(file_name.joinpath("products.csv"))
            .fillna({"iri": "https://empty.com", "BoM_id": ""})
            .iterrows()
        ]
        # Parse chemical
        pydt_chemical_compounds = [
            ChemicalCompoundPdt(
                **x[1].to_dict()
                | {
                    "reference_quantity": QuantityPdt(
                        quantity=x[1].to_dict()["reference_quantity"], unit=all_unit[x[1].to_dict()["unit"]]
                    )
                }
            )
            for x in Inventory.__read_csv(file_name.joinpath("chemical_compounds.csv"))
            .fillna({"iri": "https://empty.com", "BoM_id": ""})
            .iterrows()
        ]
        # Merge chemical and product as they should be unique by Id
        all_products = {p.name: p for p in pydt_products_parsed + pydt_chemical_compounds}
        all_boms = dict()
        for BoMId, df_bom_product in Inventory.__read_csv(file_name.joinpath("BoM.csv")).groupby("BoMId"):
            all_boms[BoMId] = BoMPdt(
                BoMId=BoMId,
                product_quantities={
                    all_products[row["Material"]].name: QuantityPdt(
                        quantity=row["Quantity"], unit=all_unit[row["Unit"]]
                    )
                    for _, row in df_bom_product.iterrows()
                },
            )
        # Now we have to create the real object
        # And associate the BoM to their respective product
        real_units = {
            u.name: u for u in (Unit(x[1].name, None if x[1].iri is None else str(x[1].iri)) for x in all_unit.items())
        }
        real_products = (
            Product(
                x[1].name,
                None if x[1].iri is None else str(x[1].iri),
                x[1].reference_quantity.to_quantity(real_units),
                bom=None,
            )
            if isinstance(x[1], ProductPdt)
            else ChemicalCompound(
                x[1].name,
                None if x[1].iri is None else str(x[1].iri),
                x[1].reference_quantity.to_quantity(real_units),
                bom=None,
            )
            for x in all_products.items()
        )
        real_product_dict = {p.name: p for p in real_products}
        real_BoMs = {
            v[1].BoMId: BoM(
                {real_product_dict[p]: p_qty.to_quantity(real_units) for p, p_qty in v[1].product_quantities.items()}
            )
            for v in all_boms.items()
        }

        for p in all_products:
            if all_products[p].BoM_id:
                real_product_dict[p].bom = real_BoMs[all_products[p].BoM_id]

        for p in real_product_dict.values():
            print(p)

        return cls(real_units, real_product_dict)
    
    

    @staticmethod
    def __read_csv(file_name: Path):
        return pd.read_csv(file_name, sep=";", decimal=".")
