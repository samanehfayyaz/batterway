from typing import List

from batterway.datamodel.Generic.Flow import Flow
from batterway.datamodel.Generic.Process import Process


class RecyclingProcess(Process):
    def __init__(self, inputs_flows: List[Flow], output_flows: List[Flow], name):
        super().__init__(name, inputs_flows, output_flows)

    def ensure_recycling_coherency(self):

        input_dfsdf=""
        output_sdfsdqf = ""
        if input_dfsdf==output_sdfsdqf:
            return True
