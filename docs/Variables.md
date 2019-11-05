# types of variables

There are two types of variables in a frof workflow; environment variables, which work the way you'd expect; and _interpolated variables_, which are user-defined (read: you-defined) and can be (optionally) injected directly into the text of a command at runtime. For an explanation of interpolated variables, how to use them, and some gotchas, check out _[Interpolation](Interpolation.md)_.

## common environment variables

| Variable Name                     | Description                                            |
| --------------------------------- | ------------------------------------------------------ |
| [`FROF_JOB_NAME`](#FROF_JOB_NAME) | The name of the currently running job                  |
| [`FROF_RUN_ID`](#FROF_RUN_ID)     | The ID of the current run of this plan (UUID)          |
| [`FROF_PLAN_ID`](#FROF_PLAN_ID)   | The ID of the plan file                                |
| `FROF_VERSION`                    | The version of the running frof package (e.g. `1.2.3`) |

### `FROF_JOB_NAME`

This is the name you provided in the .frof file, or, if you imported a job from another file, it is the slash-namespaced name of the imported file followed by the variable.

For example, in the following file:

```yml
first_job -> second_job
...
```

...the `FROF_JOB_NAME` of the first-run job is `"first_job"`.

### `FROF_RUN_ID`

This is the name of the _run_ of the current plan. In other words, if you create a frof file and run it twice with `frof myfile.frof`, each will have a different `FROF_RUN_ID`, but the same `FROF_PLAN_ID`. You can use this quality to save results to a different file based upon the ID of the run.

### `FROF_PLAN_ID`

This is _expected_ (but not guaranteed) to be the same for the same .frof file, no matter where and when the file is run. For example, if you and I both download and run a sample.frof, we would expect this variable to be the same for each of us.

Unlike the `FROF_RUN_ID`, this will not change the second time you run a .frof file! You should use this to keep track of which Plan an output came from, but you should NOT expect it to distinguish between different runs of the same file.

If a frof is running inside another frof, this will be a (`--`)-chained concatenation of the parent `FROF_PLAN_ID`s. For example, in the case of a job triply nested, this will be `[OUTERMOST_PLAN_ID]--[NEXT_PLAN_ID]--[THIS_PLAN_ID]`.

## other environment variables

| Variable Name          | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `FROF_BATCH_ITER`      | The integer order of this job's execution in its batch |
| *`FROF_PARENT_PLAN_ID` | ID of the parent Plan.                                 |
| *`FROF_PARENT_RUN_ID`  | ID of the parent Execution.                            |

*: Only set if this frof is running inside of another frof

### `FROF_BATCH_ITER`

~~For executors in which several jobs are run in a group, provides the index of this job inside that batch.~~

Will be deprecated. Do not use.
