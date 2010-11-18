#!/bin/bash

if [ $# -lt 2 ]; then
	echo "Usage:" $0 filename col
	exit
fi

filename=$1
col=$2

linenumber=`cat $filename | wc -l`
linenumberuniq=`cut -f $col $filename | sort | uniq | wc -l`

echo "total lines:" $linenumber
echo "Unique lines:" $linenumberuniq
if (( $linenumberuniq == $linenumber )); then
	echo "Unique"
else
	echo "Not Unique"
fi;

	
