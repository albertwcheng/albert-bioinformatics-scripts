#!/bin/bash

curDir=`pwd`

if [ $# -lt 2 ]; then
	pattern="*"
	if [ $# -lt 1 ]; then
		echo Usage: $0 dir '[pattern=*]'
		exit
	else
		dirGo=$1
	fi	
else
	dirGo=$1
	pattern=$2	
fi
	

cd $dirGo

for f in $pattern; do
	newF=`echo $f | tr " " "-"`
	if [ "$newF" != "$f" ]; then	
		echo "mv \"$f\" $newF"
		eval "mv \"$f\" $newF"
	fi
	
	if [ -d "$newF" ]; then
		echo $newF is folder go recursive
		$0 $newF "$pattern"
	fi
done
