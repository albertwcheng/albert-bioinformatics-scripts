#!/bin/bash


#check if program in path, return 1 yes, return 0 no
if [ $# -lt  1 ]; then
	echo $0 programName > /dev/stderr
	echo 0
	exit
fi

which $1 2>/dev/null | wc -l

