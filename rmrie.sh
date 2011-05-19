#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 filenames ...
fi

while [ $# -gt 0 ]; do
	i=$1
	shift
	if [ -e $i ]; then 
		rm -Rf $i
	fi
done