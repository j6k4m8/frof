## *Class* `StatusMonitor(abc.ABC)`


Abstract class for status-monitoring capabilities.

Do not use directly.


## *Function* `emit_status(self)`


Emit a status for the contained FrofPlan.

### Arguments
    None

### Returns
    None



## *Class* `OneLineStatusMonitor(StatusMonitor)`


A status monitor that keeps itself constrainted to a single line.

### prints

    🤔 7 jobs running, 9 remaining.

### prints

    Starting job with 17 jobs total.

### prints

    👌 0 jobs running, 0 remaining.



## *Function* `__init__(self, fe: "FrofExecutor") -> None`


Create a new OneLineStatusMonitor.



### Arguments
> - **fe** (`FrofExecutor`: `None`): The Executor to print for during runs

### Returns
    None



## *Function* `emit_status(self)`


Emit the current status of self.fe.

Prints directly to stdout. Uses emojis. This is not the most backward- compatible of all systems.

### Arguments
    None

### Returns
    None



## *Function* `launch_status(self)`


Print the current status pre-run of the Plan.

### Arguments
    None

### Returns
    None



## *Class* `FrofPlan`


FrofPlan objects hold a network of jobs to run, and manage the execution.

### with

    FrofPlan(FROF_FILE_NAME)

    FrofPlan(FROF_FILE_CONTENTS)

    FrofPlan(my_DiGraph)



## *Function* `__init__(self, frof)`


Create a new FrofPlan.

### Arguments
> - **nx.DiGraph])** (`None`: `None`): The job network to run. Can be a
        network, designed manually, or a string representation of a         plan, OR the name of a file to read for the plan.

### Returns
    None



## *Function* `as_networkx(self)`


Return this Plan as a NetworkX graph.

### Arguments
    None

### Returns
> - **nx.DiGraph** (`None`: `None`): This plan network



## *Class* `FrofExecutor(abc.ABC)`


FrofExecutors are responsible for converting a Plan to actual execution.

There might be, for example, a LocalFrofExecutor, a ClusterFrofExecutor... This is the abstract base class; do not use this class directly.


## *Class* `LocalFrofExecutor(FrofExecutor)`


A FrofExecutor that runs tasks locally in the current bash shell.

This is useful for get-it-done ease of use, but may not be the most powerful way to schedule tasks...


## *Function* `get_current_network(self) -> nx.DiGraph`


Get a pointer to the current_network of this execution.

### Arguments
    None

### Returns
> - **nx.DiGraph** (`None`: `None`): The current (mutable) network of this execution



## *Function* `get_network(self) -> nx.DiGraph`


Get a pointer to the unchanged, original network plan.

### Arguments
    None

### Returns
> - **nx.DiGraph** (`None`: `None`): The (mutable) network plan for this execution



## *Function* `get_next_jobs(self) -> List`


Get a list of the next jobs to run.

If a job belongs to a parallelism group that has a max_parallel_count, this function will only return the first max_parallel_count jobs from that group (but an unlimited number of jobs from nongroups).

### Arguments
    None

### Returns
> - **FrofJob]** (`None`: `None`): (Job Name, Job Object)



## *Function* `execute(self) -> None`


Execute the FrofPlan locally, using the current shell.

### Arguments
    None

### Returns
    None


