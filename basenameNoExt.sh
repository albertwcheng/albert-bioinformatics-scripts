#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 path
	exit
fi

bn=`basename $1`
echo `removeExt.sh $bn`

