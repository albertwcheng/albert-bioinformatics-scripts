#!/bin/bash

if [ $# -ne 1 ]; then
	echo $0 prefix
	exit 1
fi

prefix=$1


MWTAnalysis.R $prefix.exp.txt `cat $prefix.mwtcls` 0 diff `cat $prefix.mwtg1` `cat $prefix.mwtg2` `cat $prefix.mwtg2`-`cat $prefix.mwtg1` $prefix.mwt.txt

tf=`tempfile`

splitlines.py $prefix.mwt.txt 1 $prefix.mwt.sortedByfc.txt,$tf
diffcol=`colSelect.py $prefix.mwt.txt @diff`
sort -g -r -k$diffcol,$diffcol $tf >> $prefix.mwt.sortedByfc.txt

pyFilter.py $prefix.mwt.sortedByfc.txt '[@FDR]<0.05 and fabs([@diff])>=1' >  $prefix.mwt.sortedByfc.FDR0.05.fc2x.txt

