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

