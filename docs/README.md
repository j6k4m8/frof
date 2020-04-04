

## Example .frof file:

```
download_data -> parse_data -> delete_boring_parts -> write_file

download_data: 			wget http://example.com/example.tar
parse_data: 			tar xvf example.tar
delete_boring_parts: 	docker run -it -v $(pwd)/:/mnt/vin delete_parts
write_file:				mv output.txt FinalOutput-${FROF_FLOWID}.txt
```

