<p align=center><img align=center src='docs/frof.png' width=200 /></p>
<h6 align=center>frof runs other frofs</h6>

frof is a crazy-simple, zero-config tool to schedule multiple interdependent jobs.

## overview

Let's generate a simple README.md using `frof`. We create the title in one job, the contents in another job, and then combine them in a third job. The first two must run before the third, but are independent of each other.

`simple.frof`
```yml
make_heading -> combine_files
make_content -> combine_files

combine_files:  cat part_a part_b > new_readme.txt
make_heading:   echo "# frof" > part_a
make_content:   echo "frof runs other frofs" > part_b
```

## installation

```
git clone https://github.com/j6k4m8/frof.gif
cd frof
pip3 install -e .
```

Check out the [Getting Started Tutorial](docs/tutorial.md) to start getting your hands dirty.
