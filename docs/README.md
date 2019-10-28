

## Example .frof file:

```
download_data -> parse_data -> delete_boring_parts -> write_file

download_data: 			wget http://example.com/example.tar
parse_data: 			tar xvf example.tar
delete_boring_parts: 	docker run -it -v $(pwd)/:/mnt/vin delete_parts
write_file:				mv output.txt FinalOutput-${FROF_FLOWID}.txt
```



## Fan-out:

```
download_chromosomes -> [1..16] process_chromosome -> collect_results

download_chromosomes: 	scp -R http://dna.org/chromosomes/ .
process_chromosome:		python3 run_ngrams.py -f ${FROF_N} > ${FROF_N}-frof.txt
collect_results:		tar cvf results.tar *-frof-.txt
```

## Loop:

```
download_chromosomes -> [1..16, 4] process_chromosome -> collect_results
```

Means "run IDs 1 through 16, running 4 at a time".


