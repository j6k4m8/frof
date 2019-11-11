from typing import Callable, List, Tuple, Union

import abc
import copy
import hashlib
import os
import time
import uuid
from datetime import datetime

import networkx as nx
from joblib import Parallel, delayed

from .parser import FrofParser
from .statusmonitor import NullStatusMonitor

MAX_PARALLEL = 99999

__version__ = "0.0.1"


class FrofPlan:
    """
    FrofPlan objects hold a network of jobs to run, and manage the execution.

    You can invoke this with:

        FrofPlan(FROF_FILE_NAME)

        FrofPlan(FROF_FILE_CONTENTS)

        FrofPlan(my_DiGraph)

    """

    def __init__(self, frof):
        """
        Create a new FrofPlan.

        Arguments:
            frof (Union[str, nx.DiGraph]): The job network to run. Can be a
                network, designed manually, or a string representation of a
                plan, OR the name of a file to read for the plan.

        Returns:
            None

        """

        if isinstance(frof, str):
            if "\n" not in frof:
                try:
                    with open(os.path.expanduser(frof), "r") as fh:
                        self.network = FrofParser().parse(fh.read())
                except FileNotFoundError:
                    self.network = FrofParser().parse(frof)
        else:
            self.network = frof
        self.plan_id = self.generate_hash()

    def generate_hash(self) -> str:
        """
        Generate a deterministic hash for this Plan.

        This will be used as the PLAN_ID.

        Arguments:
            None

        Returns:
            str: The hash for this Plan

        """
        long_str = ".".join([node_id for node_id in self.network.nodes()])
        return hashlib.sha256(long_str.encode()).hexdigest()

    def as_networkx(self):
        """
        Return this Plan as a NetworkX graph.

        Arguments:
            None

        Returns:
            nx.DiGraph: This plan network

        """
        return copy.deepcopy(self.network)


class FrofExecutor(abc.ABC):
    """
    FrofExecutors are responsible for converting a Plan to actual execution.

    There might be, for example, a LocalFrofExecutor, a ClusterFrofExecutor...
    This is the abstract base class; do not use this class directly.
    """

    ...

    def get_next_jobs(self) -> List:
        ...

    def get_current_network(self) -> nx.DiGraph:
        ...

    def get_network(self) -> nx.DiGraph:
        ...


class LocalFrofExecutor(FrofExecutor):
    """
    A FrofExecutor that runs tasks locally in the current bash shell.

    This is useful for get-it-done ease of use, but may not be the most
    powerful way to schedule tasks...
    """

    def __init__(
        self,
        fp: Union["FrofPlan", str, nx.DiGraph],
        status_monitor: Callable = NullStatusMonitor,
        max_jobs: int = None,
    ) -> None:
        """
        Create a new LocalFrofExecutor.

        Arguments:
            fp (FrofPlan): The FrofPlan to execute. You can pass a string,
                nx.DiGraph, or FrofPlan. An initialized FrofPlan should already
                be populated with a FrofPlan#network attribute. Otherwise, all
                other argument types will be passed directly to the default
                FrofPlan constructor.
            status_monitor (StatusMonitor: NullStatusMonitor): Constructor
                for the StatusMonitor to use to track progress in this
                execution. Defaults to the NullStatusMonitor.
            max_jobs (int: None): The maximum number of jobs to run at once.
                Defaults to the number of CPUs on this machine.

        """
        self.current_network = nx.DiGraph()
        if isinstance(fp, FrofPlan):
            self.fp = fp
        else:
            self.fp = FrofPlan(fp)

        self.max_jobs = max_jobs if max_jobs else os.cpu_count()

        self.status_monitor = status_monitor(self)

    def get_current_network(self) -> nx.DiGraph:
        """
        Get a pointer to the current_network of this execution.

        Arguments:
            None

        Returns:
            nx.DiGraph: The current (mutable) network of this execution

        """
        return self.current_network

    def get_network(self) -> nx.DiGraph:
        """
        Get a pointer to the unchanged, original network plan.

        Arguments:
            None

        Returns:
            nx.DiGraph: The (mutable) network plan for this execution

        """
        return self.fp.network

    def get_next_jobs(self) -> List:
        """
        Get a list of the next jobs to run.

        If a job belongs to a parallelism group that has a max_parallel_count,
        this function will only return the first max_parallel_count jobs from
        that group (but an unlimited number of jobs from nongroups).

        Arguments:
            None

        Returns:
            Tuple[str, FrofJob]: (Job Name, Job Object)

        """
        jobs = [
            (i, j)
            for i, j in self.current_network.nodes(data=True)
            if self.current_network.in_degree(i) == 0
        ]

        parallelism_groups = {}

        result_jobs = []
        for i, job in jobs:
            if job.get("parallelism_group", None):
                if "max_parallel_count" in job and job.get("max_parallel_count"):
                    mpc = int(job.get("max_parallel_count", MAX_PARALLEL))
                else:
                    mpc = MAX_PARALLEL
                parallelism_groups[job["parallelism_group"]] = (
                    parallelism_groups.get(job["parallelism_group"], 0) + 1
                )
                if parallelism_groups[job["parallelism_group"]] <= mpc:
                    result_jobs.append((i, job["job"]))
            else:
                result_jobs.append((i, job["job"]))
        return result_jobs

    def execute(self) -> None:
        """
        Execute the FrofPlan locally, using the current shell.

        Arguments:
            None

        Returns:
            None

        """
        run_id = str(uuid.uuid4())
        self.current_network = copy.deepcopy(self.fp.network)
        self.status_monitor.launch_status()
        env = {
            "FROF_RUN_ID": run_id,
            "FROF_PLAN_ID": self.fp.plan_id,
            "FROF_VERSION": __version__,
        }
        if os.getenv("FROF_PARENT_PLAN_ID"):
            env["FROF_PARENT_PLAN_ID"] = os.getenv("FROF_PARENT_PLAN_ID")
            env["FROF_PARENT_RUN_ID"] = os.getenv("FROF_PARENT_RUN_ID")
            env["FROF_PLAN_ID"] = "{}--{}".format(
                os.getenv("FROF_PARENT_PLAN_ID"), self.fp.plan_id
            )
        while len(self.current_network):
            current_jobs = self.get_next_jobs()
            Parallel(n_jobs=self.max_jobs)(
                delayed(job.run)(
                    env_vars={
                        **env,
                        "FROF_BATCH_ITER": str(itercounter),
                        "FROF_JOB_NAME": str(i),
                    }
                )
                for itercounter, (i, job) in enumerate(current_jobs)
            )

            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            self.status_monitor.emit_status()
