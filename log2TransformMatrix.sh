#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 matrix ">" ofile
	exit 1
fi

matrix=$1

transformMatrix.py -O "log2(X)" $matrix