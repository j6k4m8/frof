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
    """
    Abstract class for status-printing capabilities.

    Do not use directly.
    """

    ...

    def emit_status(self):
        """
        Emit a status for the contained FrofPlan.

        Arguments:
            None

        Returns:
            None

        """
        ...


class OneLineStatusPrinter(StatusPrinter):
    """
    A status printer that keeps itself constrainted to a single line.

    Good for running in a CLI.
    During a run, prints:

        🤔 7 jobs running, 9 remaining.

    While the run boots, prints:

        Starting job with 17 jobs total.

    When a run has no more remaining jobs, prints:

        👌 0 jobs running, 0 remaining.

    """

    def __init__(self, fp: "FrofPlan") -> None:
        """
        Create a new OneLineStatusPrinter.



        Arguments:
            fp (FrofPlan): The Plan to print for during runs

        Returns:
            None

        """
        self.fp = fp

    def emit_status(self):
        """
        Emit the current status of self.fp.

        Prints directly to stdout. Uses emojis. This is not the most backward-
        compatible of all systems.

        Arguments:
            None

        Returns:
            None

        """
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
        """
        Print the current status pre-run of the Plan.

        Arguments:
            None

        Returns:
            None

        """
        print(f"Starting job with {len(self.fp.network)} jobs total.", end="\r")


class FrofPlan:
    """
    FrofPlan objects hold a network of jobs to run, and manage the execution.

    You can invoke this with:

        FrofPlan(FROF_FILE_NAME)

        FrofPlan(FROF_FILE_CONTENTS)

        FrofPlan(my_DiGraph)

    """

    def __init__(self, frof, status=OneLineStatusPrinter):
        """
        Create a new FrofPlan.

        Arguments:
            frof (Union[str, nx.DiGraph]): The job network to run. Can be a
                network, designed manually, or a string representation of a
                plan, OR the name of a file to read for the plan.
            status (StatusPrinter): The StatusPrinter to use for this plan.

        Returns:
            None

        """
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
        """
        Get a list of the next jobs to run.

        Arguments:
            None

        Returns:
            Tuple[str, FrofJob]: (Job Name, Job Object)

        """
        return [
            (i, j["job"])
            for i, j in self.current_network.nodes(data=True)
            if self.current_network.in_degree(i) == 0
        ]

    def run(self):
        """
        Run the plan.

        Arguments:
            None

        Returns:
            None

        """
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
                            "FROF_PLAN_ID": self.plan_id,
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
        """
        Print the plan as text.

        Useful for debugging.
        """
        self.current_network = copy.deepcopy(self.network)
        self.status.launch_status()
        while len(self.current_network):
            current_jobs = self.get_next_jobs()
            for c in current_jobs:
                print(c)
            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            print("\n")
