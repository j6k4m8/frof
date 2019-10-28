import copy
import networkx as nx
from .parser import FrofParser
import asyncio


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
            loop = asyncio.get_event_loop()
            jobs = asyncio.gather(*[job.run() for i, job in current_jobs])
            _ = loop.run_until_complete(jobs)
            # loop.close()
            for (i, _) in current_jobs:
                increment_graph.remove_node(i)
