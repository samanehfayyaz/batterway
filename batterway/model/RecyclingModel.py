import sentier_data_tools
from sentier_data_tools import Demand, RunConfig, DatasetKind, ProductIRI


class RecyclingModel(sentier_data_tools.SentierModel, ):
    provides = {
        #ProductIRI(
        #    "http://openenergy-platform.org/ontology/oeo/OEO_00010379"
        #): "hydrogen",
    }
    needs = {
        #ModelTermIRI(
        #    "https://vocab.sentier.dev/model-terms/electrolyser/capacity_factor"
        #): "capacity_factor",

        #ProductIRI("https://vocab.sentier.dev/products/electrolyzer"): "electrolyzer",
    }
    def get_recycled_product_inventory(self) -> None:
        bom_electrolysis = self.get_model_data(
            self, product=self.hydrogen, kind=DatasetKind.BOM
        )
    def __init__(self, recycled_product_iri:str):
        super().__init__(
            demand=Demand(
                recycled_product_iri
            ),
            run_config=RunConfig(

            )
        )
