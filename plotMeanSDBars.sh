#!/bin/bash

if [ $# -lt 5 ]; then
	echo $0 instats outimage Title XLabel YLabel  [ samplecol meancol minussdcol plussdcol [ moreoptions ] ]
	exit
fi

instats=$1
outimage=$2
Title=$3
XLabel=$4
YLabel=$5

#defaults:
samplecol=".sample"
meancol=".mean"
minussdcol=".sd"
plussdcol=".sd"

moreoptions=""

if [ $# -ge 6 ]; then
	if [ $# -lt 9 ]; then
		echo please provide complete options
		echo $0 instats outimage [ samplecol meancol minussdcol plussdcol ]
		exit
	fi
	
	if [ $# -ge 10 ]; then
		moreoptions=${10}
	fi
	
	samplecol=$6
	meancol=$7
	minussdcol=$8
	plussdcol=$9
fi

samplecol=`colSelect.py $instats $samplecol`
meancol=`colSelect.py $instats $meancol`
minussdcol=`colSelect.py $instats $minussdcol`
plussdcol=`colSelect.py $instats $plussdcol`

awk -v samplecol=$samplecol -v meancol=$meancol -v FS="\t" -v OFS="\t" -v minussdcol=$minussdcol -v plussdcol=$plussdcol '{if(FNR>1){if($meancol!="NA" && $minussdcol!="NA" && $plussdcol!="NA"){printf("%s\t%f\t%f\t1.0,1.0,1.0,1.0\t%f\t%f\t1.0,1.0,1.0,1.0\n",$samplecol,$meancol-$minussdcol,$minussdcol,$meancol,$plussdcol);}}}' $instats > $outimage.tmp.barin.00

matrixTranspose.py --flipV $outimage.tmp.barin.00 > $outimage.tmp.barin.01

eval "plotHBBars.py $moreoptions --title $Title --xlabel $XLabel --ylabel $YLabel $outimage.tmp.barin.01 $outimage"

rm -Rf $outimage.tmp.barin.00
rm -Rf $outimage.tmp.barin.01