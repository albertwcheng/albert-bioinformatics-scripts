#!/bin/bash

if [ $# -ne 1 ]; then
	echo $0 prefix
	exit 1
fi

prefix=$1


MWTAnalysis.R $prefix.exp.txt `cat $prefix.mwtcls` 0 diff `cat $prefix.mwtg1` `cat $prefix.mwtg2` `cat $prefix.mwtg2`-`cat $prefix.mwtg1` $prefix.mwt.txt
