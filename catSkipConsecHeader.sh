#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 file1 file2 .. fileN
	exit 1
fi

cat $1
shift

while [ $# -ge 1 ]; do
	awk 'FNR>1' $1
	shift
done


