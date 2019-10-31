from typing import List

import os
import abc
import copy
import time
import networkx as nx
from .parser import FrofParser
import asyncio
import uuid


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

    def launch_status(self):
        print(f"Starting job with {len(self.fp.network)} jobs total.", end="\r")


class FrofPlan:
    def __init__(self, frof, status=OneLineStatusPrinter):
        self.plan_id = uuid.uuid4()
        if isinstance(frof, str):
            if "\n" not in frof:
                try:
                    with open(os.path.expanduser(frof), "r") as fh:
                        self.network = FrofParser().parse(fh.read())
                except FileNotFoundError:
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
        run_id = uuid.uuid4()
        self.current_network = copy.deepcopy(self.network)
        self.status.launch_status()
        while len(self.current_network):
            current_jobs = self.get_next_jobs()
            loop = asyncio.get_event_loop()
            jobs = asyncio.gather(
                *[
                    job.run(
                        env_vars={
                            "FROF_BATCH_ITER": str(itercounter),
                            "FROF_JOB_NAME": str(i),
                            "FROF_RUN_ID": run_id,
                            "FROF_PLAN_ID": self.plan_id
                        }
                    )
                    for itercounter, (i, job) in enumerate(current_jobs)
                ]
            )
            _ = loop.run_until_complete(jobs)
            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            self.status.emit_status()

    def print_plan(self):
        self.current_network = copy.deepcopy(self.network)
        self.status.launch_status()
        while len(self.current_network):
            current_jobs = self.get_next_jobs()
            for c in current_jobs:
                print(c)
            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            print("\n")
