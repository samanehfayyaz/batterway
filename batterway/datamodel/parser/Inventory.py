from pathlib import Path

import pandas as pd

from batterway.datamodel.generic.process import RecyclingProcess
from batterway.datamodel.generic.product import BoM, ChemicalCompound, Product, ProductInstance, Unit, Quantity
from batterway.datamodel.parser.parsers import (
    BoMPdt,
    ChemicalCompoundPdt,
    ProcessLCIPdt,
    ProductPdt,
    QuantityPdt,
    UnitPdt, RecyclingProcessPdt, FixedLCIPdt,
)


class Inventory:
    def __init__(
            self,
            units: dict[str, Unit] | None,
            products: list[str:Product] | None,
            process_lcis: dict[str, RecyclingProcess] | None,
    ):
        self.units = units
        self.products = products
        self.process_lcis: dict[str, RecyclingProcess] = process_lcis

    def get_process(self,process_name:str)->RecyclingProcess:
        return self.process_lcis[process_name]
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

        for lci_id, df_lci_product in Inventory.__read_csv(file_name.joinpath("lci_relative.csv")).groupby(
            "lci_id"
        ):
            grouped_by_direction = df_lci_product.groupby(["direction"])
            relative_lc_input = [(row["influencer"], row["influenced"], row["qty"])
                                 for _, row in grouped_by_direction.get_group(("input",)).iterrows()]
            relative_lc_output = [(row["influencer"], row["influenced"], row["qty"])
                                  for _, row in grouped_by_direction.get_group(("output",)).iterrows()]
            all_process_lcis[lci_id] = ProcessLCIPdt(
                lci_id=lci_id,
                relative_lci_input=relative_lc_input,
                relative_lci_output=relative_lc_output,
            )
        pydt_fixed_lci = [
            FixedLCIPdt(
                **{
                    "lci_id":lci_id,
                    "ref_to_product_list": {rel_product:list(df_rel_target_product['product'].unique())
                for rel_product, df_rel_target_product in df_lci.groupby('ref_in_rel_lci')},
                }

            ) for lci_id,df_lci in Inventory.__read_csv(file_name.joinpath("fixedlci.csv")).groupby("lci_id")
        ]
        pydt_recycling_process = [
            RecyclingProcessPdt(
                **x[1].to_dict()
                  | {
                      "relative_lci": all_process_lcis[x[1]["relative_lci_id"]]
                  }
            )
            for x in Inventory.__read_csv(file_name.joinpath("recycling_process.csv"))
            .iterrows()
        ]
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
            stripped_bom_id = all_products[p].BoM_id.strip()
            if len(stripped_bom_id):
                real_product_dict[p].bom = real_BoMs[stripped_bom_id]

        real_fixed_lci = {
            f_lci.lci_id:{ref_label:BoM(
                {
                    real_product_dict[p]: ProductInstance(
                        real_product_dict[p],
                        Quantity(1.0,real_product_dict[p].reference_quantity.unit )
                    )
                    for p in list_of_p
                }
            ) for ref_label, list_of_p in f_lci.ref_to_product_list.items()}
            for f_lci in pydt_fixed_lci
        }
        real_recycling_process = dict()
        for r_process in pydt_recycling_process:

            fixed_lci_associated = real_fixed_lci[r_process.fixed_input_bom_id]
            relative_lci_input = {
                (real_product_dict[p2.name], real_product_dict[p[1]]): p[2] for p in
                      r_process.relative_lci.relative_lci_input for p2 in fixed_lci_associated[p[0]].products
            }
            relative_lci_output = {
                (real_product_dict[p2.name], real_product_dict[p[1]]): p[2] for p in
                r_process.relative_lci.relative_lci_output for p2 in fixed_lci_associated[p[0]].products
            }
            real_recycling_process[r_process.process_name] = RecyclingProcess(
                r_process.process_name,
                inputs_products=BoM({
                    real_product_dict[p.name]: ProductInstance(real_product_dict[p.name],
                                                               real_product_dict[p.name].reference_quantity)
                    for bom in fixed_lci_associated.values() for p in bom.products
                }),
                output_products=BoM({}),
                ref_input_to_input=relative_lci_input,
                ref_input_to_output=relative_lci_output
            )

        return cls(real_units, real_product_dict, real_recycling_process)

    @staticmethod
    def parse_possible_input(folder_path: Path):
        df_fixed_lci = Inventory.__read_csv(folder_path.joinpath("fixed_lci.csv"))

    @staticmethod
    def __read_csv(file_name: Path):
        return pd.read_csv(file_name, sep=";", decimal=".")
