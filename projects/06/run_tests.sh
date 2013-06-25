
#! /bin/bash

for infile in */*.asm; do
    cmpfile=$(echo $infile | sed s/'.asm'/'.hackcmp'/)
    outfile=$(echo $infile | sed s/'.asm'/'.hack2'/)
    
    if [ -s $cmpfile ]; then

	./hack-assembler.py $infile
	foo=$(diff $cmpfile $outfile)
	echo ${foo}
	if [ ! -z ${foo} ]; then
	    echo "input/output files differ! $infile"
	else
	    echo "Success for $infile"
	fi
    fi
done
