#!/bin/bash


if [ $# -lt 2 ]; then
	echo $0 in.fastq  out.barcodes
	exit
fi

awk '{if(FNR%4==1){split($0,a,"#"); split(a[2],b,"/"); printf("%s\n",b[1])}}' $1 | sort | uniq > $2