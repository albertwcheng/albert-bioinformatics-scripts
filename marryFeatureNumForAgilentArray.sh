#!/bin/bash

if [ $# -lt 3 ]; then
	echo $0 rawFileAsTemplate expMatrix outputFileWithFeatureNum
	exit
fi

rawFileAsTemplate=$1
expMatrix=$2
outputFileWithFeatureNum=$3

awk '(FNR>=10){printf("%s\t%s\t%s\n",$2,$3,$4);}' $rawFileAsTemplate > marryFeatureNum.map.00
#now join
joinu.py -1.Row,.Col -2.Row,.Col marryFeatureNum.map.00 $expMatrix > $outputFileWithFeatureNum
