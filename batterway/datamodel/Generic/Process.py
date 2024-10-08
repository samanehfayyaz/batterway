from typing import List

from batterway.datamodel.Generic.Product import Flow


class Process:
    def __init__(self, name, inputs_flows: List[Flow], output_flows: List[Flow]):
        self.name = name
        self.inputs = inputs_flows
        self.outputs = output_flows
