#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 "filename [numOfExtComponents=1]"
	exit
fi

filename=$1

if [ $# -gt 1 ]; then
	numOfExtComponents=$2
else
	numOfExtComponents=1
fi

pyeval.py "'.'.join('$filename'.split('.')[:-$numOfExtComponents])"