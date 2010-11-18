#!/bin/bash

#seq2fasta.sh

if [ $# -lt 2 ]; then
	echo $0 filename ofile
	exit
fi

filename=$1
ofile=$2

first=`grep F3 $filename | wc -l`
pairedEndSecond=`grep F5 $filename | wc -l` 
matePairSecond=`grep R3 $filename | wc -l`
echo -e "$filename\t$first\t$pairedEndSecond\t$matePairSecond" > $ofile