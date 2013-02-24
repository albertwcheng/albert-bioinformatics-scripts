#!/bin/bash

if [ $# -lt 2 ]; then
	echo "$0 infil[either a raw seq, a fasta or genbank] outfil"
	exit 1
fi

infile=$1
outfile=$2

fileToDo=$infile

wcLOCUS=`grep LOCUS $infile | wc -l`
if [[ $wcLOCUS == 1 ]]; then
	echo extract Seq from Genbank
	tfile1=`tempfile`
	extractSeqFromGenBankFile.py $infile > $tfile1
	fileToDo=$tfile1
fi

awk -v FS="\t" -v OFS="\t" '{if(substr($0,1,1)!=">")print;}' $fileToDo | tr "acCgt" "AttGT" > $outfile
