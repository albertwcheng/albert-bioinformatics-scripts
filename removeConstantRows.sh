#!/bin/bash

#for a matrix, remove all rows that have constant values

if [ $# -lt 2 ]; then
	echo $0 infile outfile
	exit
fi

infile=$1
outfile=$2

awk -v FS="\t" -v OFS="\t" '{toP=0;if(FNR>1){for(i=3;i<=NF;i++){if($i!=$(i-1)){toP=1; break;}}}else{toP=1;} if(toP){print;}}' $infile > $outfile