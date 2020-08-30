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
from ..job import BashJob
from ..statusmonitor import NullStatusMonitor


class FrofPlan:
    """
    FrofPlan objects hold a network of jobs to run, and manage the execution.

    You can invoke this with:

        FrofPlan(FROF_FILE_NAME)

        FrofPlan(FROF_FILE_CONTENTS)

        FrofPlan(my_DiGraph)

    """

    def __init__(self, frof, job_class=BashJob):
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
                        self.network = FrofParser().parse(
                            fh.read(), job_class=job_class
                        )
                except FileNotFoundError:
                    self.network = FrofParser().parse(frof, job_class=job_class)
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

