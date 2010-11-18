#!/bin/bash

if [ $# -lt 5 ]; then
	echo $0 "cut1flag filename1 diffFlag cut2flag filename2"
	exit
fi

cut1flag=$1
filename1=$2
diffFlag=$3
cut2flag=$4
filename2=$5

TMPDIR='/tmp'

tmpCut1file="$TMPDIR/$(basename $0).$$.1"
tmpCut2file="$TMPDIR/$(basename $0).$$.2"

eval "cut $cut1flag $filename1 > $tmpCut1file"
eval "cut $cut2flag $filename2 > $tmpCut2file"

eval "diff $diffFlag $tmpCut1file $tmpCut2file"

rm $tmpCut1file
rm $tmpCut2file
