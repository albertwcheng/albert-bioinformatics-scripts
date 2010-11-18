#!/bin/bash

if [ $# -lt 11 ]; then
	echo $0 filename chrID1 base1 start1 end1 chrID2 base2 start2 end2 minOverlap startRow >> /dev/stderr
	exit
fi

filename=$1
#echo ${10} >> /dev/stderr

awk  -v chrID1=$2 -v base1=$3 -v start1=$4 -v end1=$5 -v chrID2=$6 -v base2=$7 -v start2=$8 -v end2=$9 -v minOverlap=${10} -v FS="\t" -v OFS="\t" -v startRow=${11} 'BEGIN{}{if(FNR<startRow){print;}else{ start_1=$start1+1-base1; start_2=$start2+1-base2; end_1=$end1; end_2=$end2; if($chrID1==$chrID2){if((start_2>=start_1+minOverlap-1 && start_2<=end_1-minOverlap+1) || (end_2>=start_1+minOverlap-1 && end_2<=end_1-minOverlap+1) || (start_1>=start_2+minOverlap-1 && start_1<=end_2-minOverlap+1) || (end_1>=start_2+minOverlap-1 && end_1<=end_2-minOverlap+1)){print;}} }}' $filename  2>> /dev/stderr


