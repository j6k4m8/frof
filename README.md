# frof
frof runs other frofs

frof is a tool to schedule multiple jobs to run in parallel or sequentially. it doesn't care what tech you use; it just waits for previous tasks to finish and then runs the next command.

frof is a bmuddiputs job scheduler that uses a simple job syntax. I can't think of a simpler syntax to run large jobs:

`simple.frof`
```
make_file_a -> make_file_b -> combine_files

make_file_a:   echo "# frof" > part_a
make_file_b:   sleep 3 && echo "frof runs other frofs" > part_b
combine_files: cat part_a part_b > new_readme.txt
```

