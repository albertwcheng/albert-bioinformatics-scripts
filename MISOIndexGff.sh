#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 gffFile outputDir
	exit
fi

gffFile=$1
outputDir=$2

bsub python /lab/jaenisch_albert/Apps/yarden/MixtureIsoforms/index_gff.py --index $gffFile $outputDir