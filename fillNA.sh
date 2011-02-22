#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 infile outfile "[fill=NA]"
	echo "Fill empty cell with NA"
	exit
fi

infile=$1
outfile=$2

NA="NA"
if [[ $# == 3 ]]; then
	NA=$3
fi

awk -v FS="\t" -v OFS="\t" -v NA=$NA '{for(i=1;i<=NF;i++){if($i==""){$i=NA;}}print;}' $infile > $outfile
