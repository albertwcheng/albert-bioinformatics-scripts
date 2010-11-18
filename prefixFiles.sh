#!/bin/bash

curDir=`pwd`

if [ $# -lt 3 ]; then
	pattern="*.*"
	if [ $# -lt 2 ]; then
		dirGo='.'
		if [ $# -lt 1 ]; then
			echo Usage: $0 prefix '[dir=CurrentDir] [pattern=*.*]'
			exit
		fi
	
	else
		dirGo=$2
	fi	
else
	dirGo=$2
	pattern=$3	
fi
	

prefix=$1

cd $dirGo

for f in $pattern; do
	echo "mv $f ${prefix}${f}"
	eval "mv $f ${prefix}${f}"
done
