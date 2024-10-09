from typing import List

from batterway.datamodel.Generic.Product import Flow, ChemicalCompound

from collections import Counter


class Process:
    def __init__(self, name, inputs_flows: List[Flow], output_flows: List[Flow]):
        self.name = name
        self.inputs = inputs_flows
        self.outputs = output_flows

    def get_input_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.inputs)

    def get_output_total_mass_per_element(self):
        return self.__get_total_mass_per_element(self.outputs)
    @staticmethod
    def __get_total_mass_per_element(flows:List[Flow]):
        list_of_mass_elem = [
            Counter(input.get_total_mass_per_element())
            for input in flows if isinstance(input.product, ChemicalCompound)
        ]
        if len(list_of_mass_elem) > 0:
            map(lambda x: list_of_mass_elem[0].update(x), list_of_mass_elem[1:])
        return dict(list_of_mass_elem[0])

class RecyclingProcess(Process):
    def __init__(self, inputs_flows: List[Flow], output_flows: List[Flow], name):
        super().__init__(name, inputs_flows, output_flows)

    def ensure_recycling_coherency(self):
        input_dfsdf = ""
        output_sdfsdqf = ""
        if input_dfsdf == output_sdfsdqf:
            return True
