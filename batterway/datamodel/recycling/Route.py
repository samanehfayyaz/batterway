from typing import List

from batterway.datamodel.generic.Process import Process


class Route:
    def __init__(self, route_id, route_process_sequence:List[Process]):
        self.route_id = route_id
        self.process_sequence = route_process_sequence