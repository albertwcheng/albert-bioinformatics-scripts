#!/bin/bash

if [ $# -ne 5 ]; then
	echo $0 infile class1selector class2selector fc outfile
	exit 1
fi

infile=$1
class1selector=$2
class2selector=$3
fc=$4
outfile=$5

pyFilter.py $infile "min([$class1selector])-max([$class2selector])>=$fc or min([$class2selector])-max([$class1selector])>=$fc" > $outfile
