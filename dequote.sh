#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Usage:" $0 " infile > outfile"
	exit
fi;

cat $1 | tr -d "\"" 
