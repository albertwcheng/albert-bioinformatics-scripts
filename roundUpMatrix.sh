#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 "infile outfile"
	exit
fi

infile=$1
outfile=$2

awk -v FS="\t" -v OFS="\t" 'function roundUp(x){xf=int(x); if(x>=xf+0.5){return xf+1;}else{return xf;}}{if(FNR>1){for(i=2;i<=NF;i++){$i=roundUp($i);}}print;}' $infile > $outfile