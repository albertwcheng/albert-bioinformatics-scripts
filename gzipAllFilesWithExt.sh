#!/bin/bash

while [ $# -gt 0 ]; do
	#echo $1
	ext=$1

	for i in *.$ext; do
		if [ -e $i ]; then
			bsub -e /dev/null -o /dev/null gzip $i
		fi
	done
	shift

done