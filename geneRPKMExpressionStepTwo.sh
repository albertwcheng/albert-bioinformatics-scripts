#!/bin/bash


if [ $# -lt 4 ]; then
	echo $0 annotation samplelist setting.txt outputdir
	echo samplelist:
	echo samplename [tab] samplebam
	echo setting.txt:
	echo geneRPKMflags=
	exit
fi



annotation=$1
samplelist=$2
setting=$3
outputdir=$4

source $setting

samplenames=(`cuta.py -f1 $samplelist`)
samplebams=(`cuta.py -f2 $samplelist`)

numSamples=${#samplenames[@]};

expressionFilesInOrder=""

for((sampleI=0;sampleI<$numSamples;sampleI++));do
	samplename=${samplenames[$sampleI]}
	samplebam=${samplebams[$sampleI]}
	expressionFilesInOrder="$expressionFilesInOrder $outputdir/${samplename}.expression"
done

#echo $expressionFilesInOrder > $outputdir/expressionFilesInOrder.config

#echo $expressionFilesInOrder
echo "merge expresson files"
rm -f  $outputdir/merged.expression.txls #make sure result file not exist for multijoinu to work
jcmd="multijoinu.sh \"-1 1-6 -2 1-6\" $outputdir/merged.expression.txls $expressionFilesInOrder"
echo $jcmd
eval $jcmd

cuta.py -f'1-6,@FPKM$' $outputdir/merged.expression.txls > $outputdir/merged.expression.FPKM.txls
cuta.py -f'1-6,@log2\(FPKM\)' $outputdir/merged.expression.txls > $outputdir/merged.expression.log2FPKM.txls
