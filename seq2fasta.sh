#!/bin/bash

#seq2fasta.sh

if [ $# -lt 2 ]; then
	echo $0 inseq outfasta
	exit
fi

inseq=$1
outfasta=$2

awk '{printf("%s\n%s\n",$1,$2);}' $inseq > $outfasta