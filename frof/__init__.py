from typing import List
import abc
import copy
import networkx as nx
from .parser import FrofParser
import asyncio


class StatusPrinter(abc.ABC):
    ...

    def emit_status(self):
        ...


class OneLineStatusPrinter(StatusPrinter):
    def __init__(self, fp: "FrofPlan") -> None:
        self.fp = fp

    def emit_status(self):
        next_job_count = len(self.fp.get_next_jobs())
        if next_job_count:
            emoji = "🤔"
        else:
            emoji = "👌"
        remaining = len(self.fp.current_network)
        print(
            f"{emoji}\t {next_job_count} jobs running, {remaining} remaining.", end="\r"
        )


class FrofPlan:
    def __init__(self, frof, status=OneLineStatusPrinter):
        if isinstance(frof, str):
            self.network = FrofParser().parse(frof)
        else:
            self.network = frof

        self.current_network = nx.DiGraph()
        self.status = status(self)

    def get_next_jobs(self) -> List:
        return [
            (i, j["job"])
            for i, j in self.current_network.nodes(data=True)
            if self.current_network.in_degree(i) == 0
        ]

    def run(self):
        self.current_network = copy.deepcopy(self.network)
        while len(self.current_network):
            current_jobs = self.get_next_jobs()
            loop = asyncio.get_event_loop()
            jobs = asyncio.gather(*[job.run() for i, job in current_jobs])
            _ = loop.run_until_complete(jobs)
            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            self.status.emit_status()
