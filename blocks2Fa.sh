#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 block outfasta
	exit
fi

block=$1
outfasta=$2

awk '{printf(">%s\n%s\n",$1,$(NF-1));}' $block > $outfasta
