<p align=center><img align=center src='docs/frof.png' width=200 /></p>
<h6 align=center>frof runs other frofs</h6>

frof is a crazy-simple, zero-config tool to schedule multiple interdependent jobs.

> Note: I wrote frof as an undergraduate in 2015–2016. It was recently updated for Python 3 support, but you may discover that it has some fun surprising bugs anyway!

## overview

Let's generate a simple README.md using `frof`. We create the title in one job, the contents in another job, and then combine them in a third job. The first two must run before the third, but are independent of each other.

`simple.frof`
```yml
make_heading -> combine_files
make_content -> combine_files -> cleanup

combine_files:  cat part_a part_b > new_readme.txt
make_heading:   echo "# frof" > part_a
make_content:   echo "frof runs other frofs" > part_b
cleanup:        rm part_a part_b
```

## installation

```
git clone https://github.com/j6k4m8/frof.gif
cd frof
pip3 install -e .
```

Check out the [Getting Started Tutorial](docs/tutorial.md) to start getting your hands dirty.

# generating documentation

The documentation generator for this repository uses frof. You can see a basic example in use by running `frof make-docs.frof` from this directory.
