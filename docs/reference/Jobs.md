## *Class* `BashJob(Job)`


BashJobs manage the execution of simple commands in a local shell.

These are executed in the current working directory.


## *Function* `__init__(self, cmd: str, use_env_vars=True, env=None) -> None`


Create a new BashJob.

### Arguments
> - **cmd** (`str`: `None`): The command to execute     use_env_vars (bool: True): Whether to set environment variables     env (dict: None): Custom environment variables to use

### Returns
    None



## *Function* `run(self, env_vars=None)`


Run the command.

### Arguments
> - **env_vars** (`dict`: `None`): Custom environment variables to use

### Returns
    None



## *Function* `__str__(self) -> str`


Produce this BashJob as a string.

### Returns
> - **str** (`None`: `None`): A human-readable string



## *Function* `__repr__(self) -> str`


Produce this BashJob as a string.

### Returns
> - **str** (`None`: `None`): A human-readable string



## *Class* `NullJob(Job)`


A no-op Job class that doesn't do anything.

You can optionally add a delay, which is helpful for testing.


## *Function* `__init__(self, delay: float = 0) -> None`


Create a new NullJob.

### Arguments
> - **delay** (`float`: `0`): An optional delay when "run" is called. This lets
        you test out long-running things without actually hitting disk.

### Returns
    None


