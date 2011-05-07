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


mkdir.py $outputdir

samplenames=(`cuta.py -f1 $samplelist`)
samplebams=(`cuta.py -f2 $samplelist`)

numSamples=${#samplenames[@]};

#expressionFilesInOrder=""

for((sampleI=0;sampleI<$numSamples;sampleI++));do
	samplename=${samplenames[$sampleI]}
	samplebam=${samplebams[$sampleI]}
	echo "processing $samplename"
	cmd="geneRPKM $geneRPKMflags --label-prefix ${samplename}. --region-bed-out $outputdir/${samplename}.bed --no-block-bed-out $outputdir/${samplename}.noblock.bed --bamfile $samplebam --bedfile $annotation > $outputdir/${samplename}.expression 2>  $outputdir/${samplename}.expression.stderr"
	echo $cmd > $outputdir/${samplename}.expression.sh
	bsub bash  $outputdir/${samplename}.expression.sh
	#eval $cmd
	#expressionFilesInOrder="$expressionFilesInOrder $outputdir/${samplename}.expression"
done

#echo $expressionFilesInOrder > $outputdir/expressionFilesInOrder.config

#echo $expressionFilesInOrder
#echo "merge expresson files"
#jcmd="multijoinu.sh \"-1 1-6 -2 1-6\" $outputdir/merged.expression.txls $expressionFilesInOrder"
#echo $jcmd
#eval $jcmd
