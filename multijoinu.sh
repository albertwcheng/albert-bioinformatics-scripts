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

#protection mechanism
if [ -e $resultFile ]; then
	echo "result File existed. quit. Make sure the resultFile is not your input file. Or rm it before running this. This is a protection mechanism."
	exit
fi


jtmp0=`tempfile`
jtmp2=`tempfile`

#join first two file
cmd="joinu.py $joinparam $file1 $file2 > $jtmp0"
echo $cmd
eval $cmd

shift
shift
shift
shift
while(($#>=1)); do
	file2=$1
	shift
	cmd="joinu.py $joinparam  $jtmp0 $file2 > $jtmp2"
	echo $cmd
	eval $cmd
	rm $jtmp0
	mv $jtmp2 $jtmp0
done

mv $jtmp0 $resultFile

rm $jtmp0
rm $jtmp2
