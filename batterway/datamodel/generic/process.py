from collections import Counter
from typing import List, Tuple

from batterway.datamodel.generic.product import BoM, Product, ProductInstance, Quantity


class ProcessLCI:
    def __init__(self, id: str, input_relative_lci: dict[tuple[Product, Product], float],output_relative_lci: dict[tuple[Product, Product], float]):
        self.id: str = id
        self.input_relative_lci: dict[tuple[Product, Product], float] = input_relative_lci
        self.output_relative_lci: dict[tuple[Product, Product], float] = output_relative_lci

    def __str__(self):
        return f"{self.id} ({self.direction})" + "\n".join(
            [f"{k[0]} / {k[1]} : {v}" for k, v in self.relative_lci.items()]
        )


class Process:
    def __init__(self, name, inputs_products: BoM, output_products: BoM):
        self.name = name
        self.inputs: BoM = inputs_products
        self.outputs: BoM = output_products

    def __str__(self):
        return f"{self.name} : \n" + "\n".join(map(str, self.inputs)) + "\n" + "\n".join(map(str, self.outputs))


class RecyclingProcess(Process):
    def __init__(self, name:str, inputs_products: BoM, output_products: BoM,ref_input_to_input,ref_input_to_output):
        super().__init__(name, inputs_products, output_products)
        self.ref_input_to_output_relation: dict[tuple[Product, Product], float] = ref_input_to_output
        self.ref_input_to_input_relation: dict[tuple[Product, Product], float] = ref_input_to_input
        self.computed_output_bom: BoM|None = None
        self.computed_input_bom: BoM|None = None
        self.__ensure_coherency()

    def __ensure_coherency(self):
        if any([i_rel[0] not in self.inputs for i_rel in self.ref_input_to_input_relation]):
            raise ValueError("Input product influencing input product should be in the input")
        if any([i_rel[0] not in self.inputs for i_rel in self.ref_input_to_output_relation]):
            raise ValueError("Input product influencing output should be in the inputs")

    def __update_flow(self):
        final_bom = self.inputs
        updated_in_flow_value = dict()
        for (product_influencing, product_influenced), ratio in self.ref_input_to_input_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_in_flow_value:
                    updated_in_flow_value[product_influenced] = ProductInstance(
                        product_influenced, Quantity(0, product_influenced.reference_quantity.unit)
                    )
                updated_in_flow_value[product_influenced] += (
                    final_bom.product_quantities[product_influencing].qty * ratio
                )
        for product_influenced in updated_in_flow_value:
            product_influenced.quantity = Quantity(
                updated_in_flow_value[product_influenced], product_influenced.reference_quantity.unit
            )

        updated_out_flow_value = dict()
        for (product_influencing, product_influenced), ratio in self.ref_input_to_output_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_out_flow_value:
                    updated_out_flow_value[product_influenced] = ProductInstance(
                        product_influenced, Quantity(0, product_influenced.reference_quantity.unit)
                    )
                updated_out_flow_value[product_influenced] += (
                    final_bom.product_quantities[product_influencing].qty * ratio
                )

        for product_influenced in updated_out_flow_value:
            product_influenced.quantity = Quantity(
                updated_out_flow_value[product_influenced], product_influenced.reference_quantity.unit
            )

        self.computed_output_bom = BoM(updated_out_flow_value)
        self.computed_input_bom = BoM(updated_in_flow_value)

    def update_fixed_input_lci(self,products_qty:dict[str,float]):
        self.computed_output_bom = None
        self.computed_input_bom = None
        if not len(products_qty):
            raise ValueError("Empty inputs")
        for product,qty in products_qty.items():
            self.inputs.set_quantity_of_product(product,qty)
        self.__update_flow()

    def __str__(self):
        return super().__str__()


class Route:
    def __init__(self, route_id, route_process_sequence: List[Tuple[Tuple[Product, Process]]]):
        self.route_id = route_id
        self.process_sequence = route_process_sequence

    def ensure_consistency(self):
        output_products = None
        previous_process = None
        for process in self.process_sequence:
            if output_products is not None:
                input_products = [f.product for f in process.inputs]
                if not any(p_output in input_products for p_output in output_products):
                    raise ValueError(f"No product produced by {previous_process} used by {process}")
            output_products = [f.product for f in process.outputs]
            previous_process = process

    def __str__(self):
        return f"{self.route_id}" + ">=".join([p.name for p in self.process_sequence])


class RecyclingRoute:
    def __init__(self, route_id, route_process_sequence: List[RecyclingProcess]):
        self.route_id = route_id
        self.process_sequence = route_process_sequence

    def ensure_consistency(self):
        output_products = None
        previous_process = None
        for process in self.process_sequence:
            if output_products is not None:
                input_products = [f.product for f in process.inputs]
                if not any(p_output in input_products for p_output in output_products):
                    raise ValueError(f"No product produced by {previous_process} used by {process}")
                if process.ref_input not in input_products:
                    raise ValueError(f"Missing the reference input of {process} from {previous_process}")
            output_products = [f.product for f in process.outputs]
            previous_process = process
