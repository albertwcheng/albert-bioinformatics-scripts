#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 file1 ". . ." fileN
	exit 1
fi

while [ $# -gt 0 ]; do
	echo rename $1 as $1.bak
	mv $1 $1.bak
 	shift
done