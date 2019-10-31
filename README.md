<p align=center><img align=center src='docs/frof.png' width=200 /></p>
<h6 align=center>frof runs other frofs</h6>
<h3 align=center></h3>

frof is a tool to schedule multiple jobs to run in parallel or sequentially. it doesn't care what tech you use; it just waits for previous tasks to finish and then runs the next command.

## overview

frof is a bmuddiputs job scheduler that uses a simple job syntax. I can't think of a simpler syntax to run large jobs:

`simple.frof`
```
make_file_a -> combine_files
make_file_b -> combine_files

make_file_a:   echo "# frof" > part_a
make_file_b:   echo "frof runs other frofs" > part_b
combine_files: cat part_a part_b > new_readme.txt
```

## installation

```
git clone https://github.com/j6k4m8/frof.gif
cd frof
pip3 install -e .
```

Check out the [Getting Started Tutorial](docs/tutorial.md) to get started.
