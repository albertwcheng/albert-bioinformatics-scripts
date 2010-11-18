#!/bin/bash

if [ $# -lt 1 ]; then
	echo Usage: $0 file1 file2 ....
	exit
fi

numFiles=$#

echo "received $numFiles number of files"


while(($#>=1)); do
	fileToCheck=$1
	shift
	bsub guessSOLiDPairedMateOrSingle.sh $fileToCheck $fileToCheck.guessSOLiDP
done
