#!/bin/bash

if [ $# -lt 4 ]; then
	echo $0 mas5File mas5CallFile PACountCutOffInclusive outFile
	exit
fi

mas5File=$1
mas5CallFile=$2
PACutOff=$3
outFile=$4

awk -v FS="\t" -v OFS="\t" -v cutOff=$PACutOff '{PCall=0;for(i=1;i<=NF;i++){if($i=="P"){PCall++;}} if(FNR==1 || PCall>=cutOff){print;}}' $mas5CallFile > $outFile.mas5Call.PA$PACutOff
joinu.py -r $outFile.mas5Call.PA$PACutOff $mas5File > $outFile