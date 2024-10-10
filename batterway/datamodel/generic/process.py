from typing import List, Tuple

from batterway.datamodel.generic.product import Flow, ChemicalCompound, Product, Quantity

from collections import Counter


class Process:
    def __init__(self, name, inputs_flows: List[Flow], output_flows: List[Flow]):
        self.name = name
        self.inputs: List[Flow] = inputs_flows
        self.outputs: List[Flow] = output_flows

    def get_input_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.inputs)

    def get_output_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.outputs)
    @staticmethod
    def __get_total_mass_per_element(flows:List[Flow]):
        list_of_mass_elem = [
            Counter(input.product.get_total_mass_per_element())
            for input in flows if isinstance(input.product, ChemicalCompound)
        ]
        if len(list_of_mass_elem) > 0:
            map(lambda x: list_of_mass_elem[0].update(x), list_of_mass_elem[1:])
        return dict(list_of_mass_elem[0])

    def __str__(self):
        return f"{self.name}"

class RecyclingProcess(Process):
    def __init__(self, inputs_flows: List[Flow], output_flows: List[Flow], name, ref_input:Flow):
        super().__init__(name, inputs_flows, output_flows)
        self.ref_input_flow = ref_input
        self.ref_input_to_output_relation:dict[tuple[Product, Flow], float] = []
        self.ref_input_to_input_relation:dict[tuple[Product, Flow], float] = []

    def __ensure_coherency(self):
        if any([i_rel[1] not in self.outputs for i_rel in self.ref_input_to_output_relation]):raise ValueError("Influenced output flow not presents")
        if any([i_rel[1] not in self.inputs for i_rel in self.ref_input_to_input_relation]):raise ValueError("Influenced input flow not presents")
    def update_output_flow(self):
        final_bom = self.ref_input_flow.get_final_bom()
        updated_out_flow_value = dict()
        updated_in_flow_value = dict()
        for (product,flow),ratio in self.ref_input_to_output_relation.items():
            if product in final_bom:
                if flow not in updated_out_flow_value:
                    updated_out_flow_value[flow]= 0
                updated_out_flow_value[flow]+= ratio*final_bom[product]
        for (product,flow),ratio in self.ref_input_to_output_relation.items():
            if product in final_bom:
                if flow not in updated_in_flow_value:
                    updated_in_flow_value[flow]= 0
                updated_in_flow_value[flow]+= ratio*final_bom[product]
        for flow in updated_out_flow_value:
            flow.quantity = Quantity(updated_out_flow_value[flow],flow.quantity.unit)
        for flow in updated_in_flow_value:
            flow.quantity = Quantity(updated_in_flow_value[flow],flow.quantity.unit)

    def ensure_recycling_coherency(self):
        input_dfsdf = ""
        output_sdfsdqf = ""
        if input_dfsdf == output_sdfsdqf:
            return True


class Route:
    def __init__(self, route_id, route_process_sequence: List[Tuple[Tuple[Product,Process]]]):
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
        return f"{self.route_id}" +">=".join([p.name for p in self.process_sequence])

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