from typing import Callable, List, Tuple, Union

import abc
import copy
import hashlib
import os
import time
import threading
import uuid
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

import networkx as nx
from joblib import Parallel, delayed

from .parser import FrofParser

MAX_PARALLEL = 99999

__version__ = "0.0.1"


class StatusMonitor(abc.ABC):
    """
    Abstract class for status-monitoring capabilities.

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


class OneLineStatusMonitor(StatusMonitor):
    """
    A status monitor that keeps itself constrainted to a single line.

    Good for running in a CLI.
    During a run, prints:

        🤔 7 jobs running, 9 remaining.

    While the run boots, prints:

        Starting job with 17 jobs total.

    When a run has no more remaining jobs, prints:

        👌 0 jobs running, 0 remaining.

    """

    def __init__(self, fe: "FrofExecutor") -> None:
        """
        Create a new OneLineStatusMonitor.



        Arguments:
            fe (FrofExecutor): The Executor to print for during runs

        Returns:
            None

        """
        self.fe = fe
        self.started_time = datetime.now()
        self.total_job_count = len(self.fe.fp.as_networkx())

    def emit_status(self):
        """
        Emit the current status of self.fe.

        Prints directly to stdout. Uses emojis. This is not the most backward-
        compatible of all systems.

        Arguments:
            None

        Returns:
            None

        """
        next_job_count = len(self.fe.get_next_jobs())
        if next_job_count:
            emoji = "🤔"
        else:
            emoji = "👌"
        remaining = len(self.fe.get_current_network())

        pct = (self.total_job_count - remaining) / self.total_job_count
        print(
            f"{emoji} ———— {next_job_count} jobs running, {remaining} remaining ({int(100*pct)}%).         ",
            end="\r",
        )

    def launch_status(self):
        """
        Print the current status pre-run of the Plan.

        Arguments:
            None

        Returns:
            None

        """
        print(
            f"Starting job with {len(self.fe.get_network())} jobs total.         ",
            end="\r",
        )


class HTTPServerStatusMonitor(StatusMonitor):
    def __init__(self, fe: "FrofExecutor", port: int = 8111) -> None:
        self.fe = fe
        self.port = port

        self.started_time = datetime.now()
        self.total_job_count = len(self.fe.fp.as_networkx())

        self.app = Flask(__name__)
        CORS(self.app)
        self.app.add_url_rule("/", "home", self._home)
        self.app.add_url_rule("/status", "status", self._status)
        thread = threading.Thread(
            target=self.app.run, kwargs=dict(host="0.0.0.0", port=self.port)
        )
        thread.daemon = True
        thread.start()

    def _home(self):
        return """
        <html>
            <body>
                <div id="app"></div>
                <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
                <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
                <script>
                    function setTitle(title) {
                        if (title) {
                            document.title = title + " | frof monitor";
                        } else {
                            document.title = "frof monitor";
                        }
                    }
                    let Home = Vue.component('Home', {
                        template: `
                        <div>
                            <div class="section">
                                <h1 class="title">frof monitor</h1>
                                <h2 class="subtitle">Started at {{ started_at }}.</h2>
                                <progress class="progress is-large is-success" :value="this.percent_done" max="100">{{this.percent_done}}%</progress>
                            </div>
                            <div class="section">
                                <div class="columns">
                                    <div class="column">
                                        <div class='panel'>
                                            <div class='panel-block' v-for='job in jobs'>
                                                <span class="icon" v-if="job.status=='running'">
                                                <i class="fas fa-spinner fa-pulse"></i>
                                                </span>
                                                <span class="tag" :class='classify(job.status)'>
                                                    {{job.type}}
                                                </span>
                                                {{ job.cmd }} — {{ job.env }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        `,
                        props: {
                            'jobs': {type: Array},
                            'started_at': {type: String},
                            'percent_done': {type: Number},
                        },
                        methods: {
                            classify(s) {
                                return {
                                    "running": "is-info",
                                    "pending": ""
                                }[s];
                            }
                        }
                    });

                    var app = new Vue({
                        el: '#app',
                        components: {Home,},
                        template: `
                        <div>
                            <Home
                                :jobs="this.jobs"
                                :started_at="this.started_at"
                                :percent_done="this.pct"
                                />
                        </div>`,
                        created() {
                            console.log("creating...");
                            window.setInterval(() => {
                                fetch("[[URL]]/status").then(res => res.json()).then(res => {
                                    this.jobs = res.remaining_jobs;
                                    this.started_at = res.started_at;
                                    this.pct = res.pct * 100;
                                    setTitle(`(${Math.ceil(this.pct)}%)`)
                                }).catch(() => {
                                    this.jobs = [];
                                    this.pct = 100;
                                });
                            }, 1000);
                        },
                        data: {
                            jobs: [],
                            started_at: "unknown time",
                            pct: 0
                        }
                    });
                </script>
            </body>
        </html>
        """.replace(
            "[[URL]]", "http://0.0.0.0:8111"
        )

    def _status(self):
        next_jobs = self.fe.get_next_jobs()
        next_job_count = len(next_jobs)
        remaining_count = len(self.fe.get_current_network())
        return jsonify(
            {
                "started_at": self.started_time,
                "pct": (self.total_job_count - remaining_count) / self.total_job_count,
                "remaining_count": remaining_count,
                "running": next_job_count,
                "remaining_jobs": list(
                    [
                        {
                            "cmd": str(v["job"].cmd),
                            "type": str(type(v["job"]).__name__),
                            "status": "running" if i in [i for i, k in next_jobs] else "pending",
                            "env": v["job"].env,
                        }
                        for i, v in self.fe.get_current_network().nodes(data=True)
                    ]
                ),
            }
        )

    def launch_status(self):
        self.status = ""

    def emit_status(self):
        self.status = ""


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
        status_monitor: Callable = OneLineStatusMonitor,
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
            status_monitor (StatusMonitor: OneLineStatusMonitor): Constructor
                for the StatusMonitor to use to track progress in this
                execution. Defaults to the OneLineStatusMonitor.
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
