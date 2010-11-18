#!/bin/bash

if [ $# -lt 2 ]; then
	echo Usage: $0 file1 file2
	echo Function: swap the name of file1 and file2
	exit
fi

file1=$1
file2=$2

mv $file1 $file1.00
mv $file2 $file1
mv $file1.00 $file2
