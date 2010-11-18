#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 "filename"
	exit
fi

awk 'BEGIN{FS="\t";}(FNR==1){printf("%d\n",NF);}' $1