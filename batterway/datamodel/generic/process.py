from typing import List, Tuple

from batterway.datamodel.generic.product import ChemicalCompound, Product, Quantity, ProductInstance, BoM

from collections import Counter


class ProcessLCI():
    def __init__(self, id: str, direction: str, relative_lci: dict[tuple[Product, Product], float]):
        self.id: str = id
        self.direction: str = direction
        self.relative_lci: dict[tuple[str, str], float] = relative_lci


class Process:
    def __init__(self, name, inputs_products: BoM, output_products: BoM):
        self.name = name
        self.inputs: BoM= inputs_products
        self.outputs: BoM = output_products

    def get_input_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.inputs)

    def get_output_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.outputs)

    @staticmethod
    def __get_total_mass_per_element(flows: BoM):
        list_of_mass_elem = [
            Counter(input.product.get_total_mass_per_element())
            for input in flows if isinstance(input.product, ChemicalCompound)
        ]
        if len(list_of_mass_elem) > 0:
            map(lambda x: list_of_mass_elem[0].update(x), list_of_mass_elem[1:])
        return dict(list_of_mass_elem[0])

    def __str__(self):
        return f"{self.name} : \n" + "\n".join(map(str, self.inputs)) + "\n" + "\n".join(map(str, self.outputs))


class RecyclingProcess(Process):
    def __init__(self, inputs_products: BoM, output_products: BoM, name):
        super().__init__(name, inputs_products, output_products)
        self.ref_input_to_output_relation: dict[tuple[Product, Product], float] = []
        self.ref_input_to_input_relation: dict[tuple[Product, Product], float] = []

    def set_influencing_input_process(self, input_to_input_relation: dict[tuple[Product, Product], float]):
        self.ref_input_to_input_relation = input_to_input_relation

    def set_influencing_output_process(self, input_to_output_relation: dict[tuple[Product, Product], float]):
        self.ref_input_to_output_relation = input_to_output_relation

    def __ensure_coherency(self):
        if any([i_rel[1] not in self.outputs for i_rel in self.ref_input_to_output_relation]): raise ValueError(
            "Influenced output flow not presents")
        if any([i_rel[1] not in self.inputs for i_rel in self.ref_input_to_input_relation]): raise ValueError(
            "Influenced input flow not presents")
        if any([i_rel[0] not in self.inputs for i_rel in self.ref_input_to_input_relation]): raise ValueError(
            "Input influencing product should be in the input")
        if any([i_rel[0] not in self.inputs for i_rel in self.ref_input_to_output_relation]): raise ValueError(
            "Output influencing product should be in the inputs")

    def update_flow(self):
        final_bom = self.inputs
        updated_in_flow_value = dict()
        for (product_influencing, product_influenced), ratio in self.ref_input_to_input_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_in_flow_value:
                    updated_in_flow_value[product_influenced] = ProductInstance(product_influenced,Quantity(0,product_influenced.reference_quantity.unit))
                updated_in_flow_value[product_influenced] += final_bom.product_quantities[product_influencing].qty * ratio
        for product_influenced in updated_in_flow_value:
            product_influenced.quantity = Quantity(updated_in_flow_value[product_influenced],
                                                   product_influenced.reference_quantity.unit)

        updated_out_flow_value = dict()
        for (product_influencing, product_influenced), ratio in self.ref_input_to_output_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_out_flow_value:
                    updated_out_flow_value[product_influenced] = ProductInstance(product_influenced,Quantity(0,product_influenced.reference_quantity.unit))
                updated_out_flow_value[product_influenced] +=  final_bom.product_quantities[product_influencing].qty * ratio


        for product_influenced in updated_out_flow_value:
            product_influenced.quantity = Quantity(updated_out_flow_value[product_influenced],
                                                   product_influenced.reference_quantity.unit)

        # cheat
        self.final_output_bom = updated_out_flow_value
        self.final_input_bom = updated_in_flow_value

    def ensure_recycling_coherency(self):
        input_dfsdf = ""
        output_sdfsdqf = ""
        if input_dfsdf == output_sdfsdqf:
            return True
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
    
