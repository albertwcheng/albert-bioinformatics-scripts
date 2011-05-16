#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 filenames ...
fi

while [ $# -gt 0 ]; do
	i=$1
	shift
	rm -R $i
done