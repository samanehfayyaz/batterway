from pathlib import Path

import pandas as pd

from batterway.datamodel.generic.process import ProcessLCI
from batterway.datamodel.generic.product import BoM, ChemicalCompound, Product, ProductInstance, Unit
from batterway.datamodel.parser.parsers import (
    BoMPdt,
    ChemicalCompoundPdt,
    ProcessLCIPdt,
    ProductPdt,
    QuantityPdt,
    UnitPdt,
)


class Inventory:
    def __init__(
        self,
        units: dict[str, Unit] | None,
        products: list[str:Product] | None,
        process_lcis: dict[str, ProcessLCI] | None,
    ):
        self.units = units
        self.products = products
        self.process_lcis = process_lcis

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

        all_process_lcis = dict()

        for (lci_id, direction), df_lci_product in Inventory.__read_csv(file_name.joinpath("lci_relative.csv")).groupby(
            ["lci_id", "direction"]
        ):
            all_process_lcis[(lci_id, direction)] = ProcessLCIPdt(
                lci_id=lci_id,
                direction=direction,
                relative_lci=[
                    (row["influencer"], row["influenced"], row["qty"]) for _, row in df_lci_product.iterrows()
                ],
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
                {
                    real_product_dict[p]: ProductInstance(real_product_dict[p], p_qty.to_quantity(real_units))
                    for p, p_qty in v[1].product_quantities.items()
                }
            )
            for v in all_boms.items()
        }

        for p in all_products:
            strippe_dbom_id = all_products[p].BoM_id.strip()
            if len(strippe_dbom_id):
                real_product_dict[p].bom = real_BoMs[strippe_dbom_id]

        real_process_lcis = {
            l[0]: ProcessLCI(
                id=l[0][0],
                direction=l[0][1],
                relative_lci={(real_product_dict[t[0]], real_product_dict[t[1]]): t[2] for t in l[1].relative_lci},
            )
            for l in all_process_lcis.items()
        }

        return cls(real_units, real_product_dict, real_process_lcis)

    @staticmethod
    def parse_possible_input(folder_path: Path):
        df_fixed_lci = Inventory.__read_csv(folder_path.joinpath("fixed_lci.csv"))

    @staticmethod
    def __read_csv(file_name: Path):
        return pd.read_csv(file_name, sep=";", decimal=".")
