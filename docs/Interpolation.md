# interpolated variables

As you saw in the [Beginner's Tutorial](tutorial.md), you can inline your own custom values by using frof interpolated variables. It looks something like this:

```yml
first_job(&var) -> second_job

first_job:  touch {{&var}}.txt
second_job: echo "Done!" > status.out

&var: ["FOO", "BAR"]
```

In this example, _two_ files will be created in the `first_job` stage: `FOO.txt` and `BAR.txt`. The values of `&var`, as defined in that last line, `&var: ["FOO", "BAR"]`, are _directly_ interpolated into the text of the job at runtime. This isn't an environment variable; it is a string interpolation. (This means it works wherever that string appears in your command definition, even if it's in non-bash code.)

## tricks

Variable definition is actually just inline Python, which means that any valid stdlib Python code is a valid variable definition. The following are all valid ways to define a variable in a .frof file:

```python
&foo:   list(range(0, 100))
&bar:   open("bar.txt", 'r').readlines()
&baz:   [f"BAZ_{i}" for i in ["X", "Y", "Z"]]
```

The only restriction is that the variable must be of List type; i.e. iterators aren't fair game, nor are dictionaries or other Iterables.

## gotchas

### Your arrays shouldn't include duplicates

In the following example:

```yml
first_job(&var) -> second_job

first_job:  touch {{&var}}.txt
second_job: echo "Done!" > status.out

&var: ["FOO", "BAR", "FOO"]
```

...only two commands are executed: `touch FOO.txt` and `touch BAR.txt`. Even though the `FOO` variable appears twice in the definition of `&var`, it is only executed once. This "deduplication" step is intended as a feature, but can be confusing if you expect frof to run each _item_, rather than each _value_ of the definition. Take another example:

```yml
A(&i) -> B

A: cat {{&i}} > output.txt
B: mv output.txt final_output.txt

&i: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
```

This command will only run a _single_ job in the `A` stage.
