#!/bin/bash

if [[ $# != 4 ]]; then
	echo $0 "cdtFile outFile scale[e.g., 10x10] contrast[e.g., 1.0]"
	exit
fi

cdtFile=$1
outFile=$2
scale=$3
contrast=$4


echo JAVATREEVIEW at  $JAVATREEVIEWPATH
java -jar $JAVATREEVIEWPATH -r $cdtFile -- -o $outFile -s $scale -a 0 -c $contrast