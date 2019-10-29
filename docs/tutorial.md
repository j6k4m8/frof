# basic tutorial

In this short tutorial we are going to make a simple job. This assumes that you have already installed `frof` (see section above).

Our goal is to count the number of basepairs in a stretch of DNA. We haven't collected our DNA sample yet, so we'll start with a simple job to mock the real data.

(All of the code samples in this tutorial are the COMPLETE `tutorial.frof` unless marked otherwise.)

```yml
get_DNA:   python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
```

In other words, this creates a DNA strand of length 100. Great! Now we need to count the occurrences of each base-pair. Let's start with `A`. (Note that these jobs are invoking Python from the command-line, but you could also call an already-existing script.)

```yml
get_DNA:   python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_As:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "A"]))' > A
```

We need to indicate that task `count_As` should happen only _after_ `get_DNA`. To do this, we can start drawing a graph:

```yml
get_DNA -> count_As

get_DNA:   python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_As:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "A"]))' > A
```

Now let's repeat that for the other bases:

```yml
get_DNA -> count_As
get_DNA -> count_Ts
get_DNA -> count_Gs
get_DNA -> count_Cs

get_DNA:   python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_As:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "A"]))' > A
count_Ts:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "T"]))' > T
count_Gs:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "G"]))' > G
count_Cs:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "C"]))' > C
```

There is a clever part here and a silly part here:

The clever part is that frof will see that `get_DNA` is repeated in multiple edges, and since it's the same job referenced in each line, it'll only run it once. Clever!

The silly part is that we have four identical jobs — with the exception of which base they're counting. We can easily fix this by using frof variables. In particular, we'll use the `FROF_JOB_PARAM` variable, _like so_:

```yml
get_DNA -> count_base(&bases)

get_DNA:     python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_base:  python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "{{&bases}}"]))' > {{&bases}}

&bases:      ["A", "T", "G", "C"]
```

Here, `&bases` is a variable (indicated by the `&` prefix); we run the `count_base` job on each of the values in the `&bases` array. Additionally, all occurrences of that variable name in the job itself will be interpolated and interpreted as the assigned runtime value. In other words, the job will be run as though it said, for example:

```bash
python3 -c 'print(len([i for i in open("DNA.txt", "r").read() if i == "A"]))' > A
```

(If you don't like this, you can toggle interpolation off. You'll still have access to this parameter value in the `$FROF_JOB_PARAM` environment variable, although you can optionally toggle that off, too.)

Finally, let's collect these values and then clean up after ourselves:

```yml
get_DNA -> count_base(&bases) -> collect_results -> clean_up(&bases)

get_DNA:            python3 -c 'import random; print("".join(random.choice("ATGC") for _ in range(100)))' > DNA.txt
count_base:         python3 -c 'print("{{&bases}} =", len([i for i in open("DNA.txt", "r").read() if i == "{{&bases}}"]))' > {{&bases}}
collect_results:    cat A T G C > results.txt
clean_up:           rm {{&bases}}

&bases:      ["A", "T", "G", "C"]

```

Note that the final step could also be written `rm A T G C`, but we got to re-use our `&bases` definition in a second job! And that's neat.

When our team eventually collects real sequences, we can simply replace the definition of `get_DNA` with the real deal. And if it turns out that it takes more than a few steps to get our hands on that sequence, we can even call another frof file from within this frof file ([[Tutorial Forthcoming]](#)). frofs within frofs! That's why it's called that, ya?
