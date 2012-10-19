#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 infile jobname
	exit
fi

infile=$1
jobname=$2

runCombinations.py bsub pyClusterArray.py "--top-sd 5000|--top-sd 1000|--top-sd 500|" "--center-gene a|--center-gene m|" "--normalize-gene|" -p -j $jobname $infile "c|s" "a|m"