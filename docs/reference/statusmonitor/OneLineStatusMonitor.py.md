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

