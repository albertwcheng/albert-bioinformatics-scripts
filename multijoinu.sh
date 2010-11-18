#!/bin/bash

#multijoinu.sh
#uses joinu.py

if [ $# -lt 4 ]; then
	echo Usage: $0 parampass_to_joinu.py resultFile file1 file2 ...
	joinu.py
	exit
fi

joinparam=$1
resultFile=$2
file1=$3
file2=$4
limiter=$#

#join first two file
cmd="joinu.py $joinparam $file1 $file2 > jtmp.00"
echo $cmd
eval $cmd

shift
shift
shift
shift
while(($#>=1)); do
	file2=$1
	shift
	cmd="joinu.py $joinparam jtmp.00 $file2 > jtmp2.00"
	echo $cmd
	eval $cmd
	rm jtmp.00
	mv jtmp2.00 jtmp.00
done

mv jtmp.00 $resultFile
