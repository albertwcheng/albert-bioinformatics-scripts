#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 CDTFile "[OutMatrix:default CDTFile/.cdt/.mat]"
	exit
fi

CDTFile=$1

if [ $# -ge 2 ]; then
OutMatrix=$2
else
OutMatrix=${CDTFile/.cdt/}
OutMatrix=${OutMatrix/.CDT/}.mat
fi

cuta.py -f1,4-_1 $CDTFile | awk '$1!="AID" && $1!="EWEIGHT"' > $OutMatrix #'FNR!=2 && FNR!=3'

