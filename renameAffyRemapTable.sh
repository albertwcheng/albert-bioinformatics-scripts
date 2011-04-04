#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 infile outfile [samRemapper]
	exit
fi

infile=$1
outfile=$2

if [ $# -ge 3 ]; then
	samRemapper=$3
else
	samRemapper="not-exists"
fi


awk -v FS="\t" -v OFS="\t" '{if(FNR==1){$1="GeneName";}else{gsub(/\_at/,"",$1);}print;}' $infile > $outfile

if [ -e $samRemapper ]; then
	mv $outfile $outfile.00
	replacer.py $outfile.00 $samRemapper > $outfile
	rm $outfile.00
fi

