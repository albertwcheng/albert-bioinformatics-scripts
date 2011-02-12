#!/bin/bash

if [ $# -lt 3 ]; then
	echo $0 inputSeq outputDir "splits[0=no splitting]"
	exit
fi

inputSeq=$1
outputDir=$2
splits=$3
splitsDir=`abspath.py $outputDir/splits`
evidenceDir=`abspath.py $outputDir/evidence`
workingsDir=`abspath.py $outputDir/workings`

mkdir $outputDir
outputDir=`abspath.py $outputDir`

mkdir $splitsDir
mkdir $evidenceDir
mkdir $workingsDir

splitLines=`pyeval.py "$splits*2"`

if [ $splits -le 0 ]; then
	echo "no split. just link"
	ln $inputSeq $splitsDir
else
	echo "spliting sequences into $splitLines by split -l $splitLines $inputSeq $splitsDir/$inputSeq"
	split -l $splitLines $inputSeq $splitsDir/$inputSeq

fi

cd $splitsDir

for seq in *; do
	echo "copying working dir $workingsDir/$seq"
	cp -R ${CPC_HOME}/working $workingsDir/$seq
	mkdir $evidenceDir/$seq/
	echo "submit job bsub run_predict.sh $seq $outputDir/$seq.resultTab $workingsDir/$seq $evidenceDir/$seq/"
	bsub run_predict.sh $seq $outputDir/$seq.resultTab $workingsDir/$seq $evidenceDir/$seq/
done