#!/bin/bash

if [[ $# != 1 ]]; then
	echo $0 inbam
	exit
fi

inbam=$1


outdir=`absdirname.py $inbam`
inbambn=`basename $inbam`

tmpfile=`tempfile`
tfbn=`basename $tmpfile`

echo "converting bam to bed"
bamtools convert -format bed -in $inbam -out $tmpfile

echo "converting bed to ylf"
BED2YoungLabFormat.py $tmpfile $outdir ylf

mv $outdir/$tfbn.ylf $outdir/$inbambn.ylf

echo "clean up"
rm $tmpfile
echo "<Done>"