#!/bin/bash

if [ $# -lt 1 ]; then
	echo Usage: $0 file ....
	exit
fi

numFiles=$#




for ((i = 1 ; i <= $numFiles ; i++)); do
	
	fil=$1
	echo operating on $fil
	shift
	awk 'function ltrim(s) { sub(/^[ \t]+/, "", s); return s } function rtrim(s) { sub(/[ \t]+$/, "", s); return s } function trim(s)  { return rtrim(ltrim(s)); } {if(length(trim($0))>0){print;}}' $fil > trim.00
	rm $fil
	mv trim.00 $fil
done
