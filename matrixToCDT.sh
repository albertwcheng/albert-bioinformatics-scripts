#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 inMatrix outCDT
	exit
fi

inMatrix=$1
outCDT=$2

awk -v FS="\t" -v OFS="\t" '{if(FNR==1){ncol=NF; for(i=ncol;i>=2;i--){$(i+2)=$i;}  $3="GWEIGHT"; $2="NAME"; $1="GENEID"; print;   $1="EWEIGHT";$2="";$3="";for(i=4;i<=ncol+2;i++){$i="1.000000"}print;}else{for(i=ncol;i>=2;i--){$(i+2)=$i;} $3="1.000000"; $2=$1;print;}}' $inMatrix > $outCDT