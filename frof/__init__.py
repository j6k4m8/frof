import copy
import networkx as nx
from .parser import FrofParser


class FrofPlan:
    def __init__(self, frof):
        if isinstance(frof, str):
            self.network = FrofParser().parse(frof)
        else:
            self.network = frof

    def run(self):
        increment_graph = copy.deepcopy(self.network)
        while len(increment_graph):
            current_jobs = [
                (i, j["job"])
                for i, j in increment_graph.nodes(data=True)
                if increment_graph.in_degree(i) == 0
            ]
            for i, job in current_jobs:
                job.run()
                increment_graph.remove_node(i)
