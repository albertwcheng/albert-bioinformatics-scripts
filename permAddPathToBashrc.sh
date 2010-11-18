#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 pathToAdd [kind: PATH, LD_LIBRARY_PATH, C_INCLUDE_PATH]
	exit
fi

pathToAdd=$1
pathToAdd=`abspath.py $pathToAdd`

if [ $# -ge 2 ]; then
	kind=$2
else
	kind="PATH"
fi

cmmd="export $kind=\${$kind}:$pathToAdd"
echo $cmmd
eval $cmmd

echo "" >> ~/bashrc
echo "" >> ~/.bashrc
echo $cmmd >> ~/bashrc
echo $cmmd >> ~/.bashrc

