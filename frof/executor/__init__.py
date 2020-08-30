from typing import Callable, Union
import abc
import networkx as nx
from joblib import Parallel, delayed
from typing import Callable, List, Tuple, Union

import abc
import copy
import hashlib
import os
import time
import uuid
from datetime import datetime

import networkx as nx

from ..parser import FrofParser
from ..plan import FrofPlan
from ..job import BashJob, SlurmJob
from ..statusmonitor import NullStatusMonitor
from ..version import __version__

MAX_PARALLEL = 99999

_HOME = os.path.expanduser("~")


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
                        "HOME": _HOME,
                    }
                )
                for itercounter, (i, job) in enumerate(current_jobs)
            )

            for (i, _) in current_jobs:
                self.current_network.remove_node(i)
            self.status_monitor.emit_status()


class SlurmFrofExecutor(abc.ABC):
    """
    FrofExecutors are responsible for converting a Plan to actual execution.

    There might be, for example, a LocalFrofExecutor, a ClusterFrofExecutor...
    This is the abstract base class; do not use this class directly.
    """

    def __init__(
        self,
        fp: Union["FrofPlan", str, nx.DiGraph],
        status_monitor: Callable = NullStatusMonitor,
        max_jobs: int = None,
    ) -> None:
        if isinstance(fp, FrofPlan):
            self.fp = fp
        else:
            self.fp = FrofPlan(fp, job_class=SlurmJob)
        self.status_monitor = status_monitor(self)
        self.max_jobs = max_jobs

    def get_next_jobs(self) -> List:
        return []

    def get_current_network(self) -> nx.DiGraph:
        return nx.DiGraph()

    def get_network(self) -> nx.DiGraph:
        return self.fp.as_networkx()

    def execute(self) -> None:
        network = self.get_network()
        slurm_lookups = {}
        nodes_to_run = {i: job["job"] for i, job in network.nodes(data=True)}
        while len(nodes_to_run) > 0:
            nodes_to_remove = []
            for i, job in nodes_to_run.items():
                # "Submitted batch job 1097"
                if all([dep in slurm_lookups for dep, _ in network.in_edges(i)]):
                    deps = ":".join(
                        [dep in slurm_lookups for dep, _ in network.in_edges(i)]
                    )
                    slurm_id = job.run(
                        extra_args=(
                            {"dependency": f"afterok:{deps}", "partition": "htc-amd",}
                            if deps
                            else {"partition": "htc-amd"}
                        )
                    ).split()[-1]
                    slurm_lookups[i] = slurm_id
                    nodes_to_remove.append(i)
            for i in nodes_to_remove:
                nodes_to_run.pop(i)
