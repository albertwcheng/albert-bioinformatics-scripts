#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 filename "col[-1:whole line]" "filterRep=n[default:2] all repeated>=n" "headn[default:10,-1:all]"
	exit
fi

if [ $# -ge 3 ]; then
	filterRep=$3
else
	filterRep=2
fi

if [ $# -ge 4 ]; then
	headn=$4
else
	headn=10
fi

filename=$1
col=$2

if [[ $col == "-1" ]]; then
	cutafilter="cat $filename"
else
	cutafilter="cuta.py -f\"$col\" $filename "
fi

if [[ $filterRep == 0 ]]; then
	filterRepCmd=""
else
	filterRepCmd=" | awk \"\\\$1>=($filterRep)\""
fi

if [[ $headn == -1 ]]; then
	headnfilter=""
else
	headnfilter=" | head -n $headn"
fi

echo "-----$filename-----"
eval "$cutafilter | sort | uniq -c $filterRepCmd | sort -k1,1 -r -g  $headnfilter"
echo "-------------------"


