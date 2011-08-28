#!/bin/bash

if [ $# -lt 6 ]; then
	echo $0 instats outimage PlotCol Title XLabel YLabel [ samplecol [ moreoptions ] ]
	exit
fi


samplecol=".sample"
moreoptions=""

if [ $# -ge 7 ]; then
	samplecol=$7
fi

if [ $# -ge 8 ]; then
	moreoptions=$8
fi


instats=$1
outimage=$2
plotcol=$3
Title=$4
XLabel=$5
YLabel=$6

samplecol=`colSelect.py $instats $samplecol`
plotcol=`colSelect.py $instats $plotcol`

awk -v samplecol=$samplecol -v FS="\t" -v OFS="\t" -v plotcol=$plotcol '{if(FNR>1){printf("%s\t%f\t%f\t1.0,1.0,1.0,1.0\n",$samplecol,0,$plotcol);}}' $instats > $outimage.tmp.barin.00

matrixTranspose.py --flipV $outimage.tmp.barin.00 > $outimage.tmp.barin.01

eval "plotHBBars.py $moreoptions --title $Title --xlabel $XLabel --ylabel $YLabel $outimage.tmp.barin.01 $outimage"


rm -Rf $outimage.tmp.barin.00
rm -Rf $outimage.tmp.barin.01