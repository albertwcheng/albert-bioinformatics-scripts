#!/bin/bash

if [ $# -lt 3 ]; then
	echo $0 infile maxValueTo outfile
	exit
fi

infile=$1
maxValueTo=$2
outfile=$3

awk -v FS="\t" -v OFS="\t" -v maxValueTo=$maxValueTo '{if(FNR>1){maxValue=$2; for(i=3;i<=NF;i++){if($i>maxValue){maxValue=$i}} for(i=1;i<=NF;i++){$i=float($i)/maxValue*maxValueTo;}} print;}' $infile > $outfile