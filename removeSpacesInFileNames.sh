#!/bin/bash

curDir=`pwd`
spaceTo="_"
pattern="*"

if [ $# -lt 3 ]; then

	if [ $# -lt 2 ]; then
	
		if [ $# -lt 1 ]; then
			echo Usage: $0 dir '[pattern=*] [spaceTo=_]'
			exit
		else
			dirGo=$1
		fi	
	else
		dirGo=$1
		pattern=$2	
	fi
else
	dirGo=$1
	pattern=$2
	spaceTo=$3
fi
	

cd $dirGo

for f in $pattern; do
	newF=`echo $f | tr " " "$spaceTo"`
	echo $f $newF
	if [ "$newF" != "$f" ]; then	
		echo "mv \"$f\" $newF"
		eval "mv \"$f\" $newF"
	fi
	
	if [ -d "$newF" ]; then
		echo $newF is folder go recursive
		$0 $newF "$pattern"
	fi
done
