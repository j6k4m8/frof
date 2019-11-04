# advanced tutorial

In this tutorial, we will expand upon the use-case we started in the [previous tutorial](tutorial.md). If you are unfamiliar with frof, or haven't read that tutorial yet, you may want to go back and read the [previous tutorial](tutorial.md) before continuing.

---

We will address a few new concepts in this tutorial:

- embedding frofs in other frofs
- handling concurrent jobs, and limiting how many jobs run at once
- a deeper understanding of how to use [variables](Variables.md)

When we last left our hero, we had the following .frof file:

```yml
get_DNA -> count_base(&bases) -> collect_results -> clean_up(&bases)

get_DNA:            python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_base:         python3 -c 'print("{{&bases}} =", len([i for i in open("DNA.txt", "r").read() if i == "{{&bases}}"]))' > {{&bases}}
collect_results:    cat A T G C > results.txt
clean_up:           rm {{&bases}}

&bases:      ["A", "T", "G", "C"]

```

For the sake of this tutorial, we'll simplify this .frof file for readability, and pretend that these scripts have been converted into Python scripts (.py files). If you are bad at pretending, you can follow along with the files in `test/advanced/`.

Now our .frof looks like this:

```yml
get_DNA -> count_base(&bases) -> collect_results -> clean_up(&bases)

get_DNA:            ./getDNA.py > DNA.txt
count_base:         ./countBases.py > {{&bases}}
collect_results:    cat A T G C > results.txt
clean_up:           rm {{&bases}}

&bases:      ["A", "T", "G", "C"]
```

One important change is that the `countBases.py` script can no longer use the `{{&bases}}` interpolation (as explained in [this guide](Interpolation.md)). Instead, we must read the environment variable `$FROF_JOB_PARAM` (with `os.getenv("FROF_JOB_PARAM")`).

Our motivating use-case for this tutorial is the need to process 100 DNA files (100 outputs from `getDNA.py`). There are a few ways we could do this:

The first way to do this is to create a new frof &variable and iterate over 100 DNA files. This isn't totally crazy, but it means that our file is about to get super complicated, as it will have to handle multiple fan-out and fan-in sequences.

A simpler way to handle this is to keep this file as it is, but create a "parent" frof file that calls this one 100 times.

The dumb-simple way to do this looks like this:

`run-all.frof`
```yml
A(&iter)

A: frof DNA.frof

&iter: list(range(100))
```

Note that we cast our `&iter` variable definition to a list; this is required. See [this guide](Variables.md) for more information on frof variables.

This looks super simple: We create a graph with only one node and zero edges, comprised solely of job `A`, which runs 100 times, and calls `frof DNA.frof` each time.

But under the hood, frof is doing a few things to make our lives easier. For one, isolates each job from the others, which means you could foreseeably run each on a different compute node in a cluster. (So far, we've been using the default `FrofExecutor`, `LocalFrofExecutor`, which runs everything in the same shell; but you can also use a cluster-based executor.)

Writing your plans in this way means that you no longer have to worry about multiple "forks" of the same graph; here, each graph is a very simple path through a small number of nodes; or in the case of `run-all.frof`, a single node.

But there is a problem: If you run `frof run-all.frof`, then if your computer is anything like mine, it'll choke hard on trying to run all of those jobs simultaneously. That's because, like in our previous tutorial, in this example, `run-all.frof` notates 100 parallelizable jobs. If you don't tell frof otherwise, it'll try to run these at the same time. This is great for cluster-based execution, but it's super sucky for local execution.

Luckily, there's a way to fix this problem: `frof` nodes can have a "maximum parallelism" annotation, which the executor will use to determine how many of that job to run simultaneously.

Let's update our file to reflect that:

`run-all.frof`
```yml
A(&iter, 4)

A: frof DNA.frof

&iter: list(range(100))
```

Note the `(&iter, 4)` This notation means to run through the `&iter` variable in groups of 4. It'll take something like 25 cycles — give or take a few — to get through the whole list of possible values. (I say "give or take a few" because frof will kick off the next job as soon as there's an available slot, so you can imagine it more like a "channel" of continuous jobs than a "round" where 4 are run to completion before the next four start.) If we run this, we'll see that it may take a bit longer for all jobs to be queued, but it'll keep our CPUs operating at optimal capacity rather than some insane clogged density.

This takes a little bit of tweaking, since the optimal number of parallel jobs is not necessarily the same as the number of CPUs on your machine. For more details, see [here](Parallelism.md).

The next issue we need to deal with is that each of these runs conflicts with the other runs because they all try to write to the same filenames. All of these jobs are competing for `DNA.txt`, `results.txt`, `A`, `T`, `C`, and `G`.

In order to deconflict, we can use the `$FROF_RUN_ID` environment variable to distinguish between files from different runs. Check it out:

`DNA.frof`
```yml
get_DNA -> count_base(&bases) -> collect_results -> clean_up(&bases)

get_DNA:            ./getDNA.py > ${FROF_RUN_ID}-DNA.txt
count_base:         ./countBases.py > ${FROF_RUN_ID}-{{&bases}}
collect_results:    cat ${FROF_RUN_ID}-A ${FROF_RUN_ID}-T ${FROF_RUN_ID}-G ${FROF_RUN_ID}-C > ${FROF_RUN_ID}-results.txt
clean_up:           rm ${FROF_RUN_ID}-{{&bases}}

&bases:      ["A", "T", "G", "C"]
```
