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



## *Function* `generate_hash(self) -> str`


Generate a deterministic hash for this Plan.

This will be used as the PLAN_ID.

### Arguments
    None

### Returns
> - **str** (`None`: `None`): The hash for this Plan



## *Function* `as_networkx(self)`


Return this Plan as a NetworkX graph.

### Arguments
    None

### Returns
> - **nx.DiGraph** (`None`: `None`): This plan network

