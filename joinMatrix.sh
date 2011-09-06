#!/bin/bash

if [ $# -lt 3 ]; then
	echo "$0 inMatrix outMatrix rowJoiner [ colJoiner [ rowJoinOpts [ colJoinOpts ] ] ]"
	echo "join opts: (from joinu.py)"
	joinu.py #no args to trigger help message
	exit
fi 

rowJoinOpts=""
colJoinOpts=""

inMatrix=$1
rowJoiner=$3
outMatrix=$2

colJoiner=$rowJoiner

if [ $# -ge 4 ]; then
	colJoiner=$4
	if [ $# -ge 5 ]; then
		rowJoinOpts=$5
		if [ $# -ge 6 ]; then
			colJoinOpts=$6
		fi
	fi

fi

#now the real stuff

tmp1=`tempfile` #get temp file tmp1
#first rowjoin
cmd="joinu.py $rowJoinOpts $rowJoiner $inMatrix > $tmp1"
eval $cmd

#cat $tmp1

tmp2=`tempfile`
matrixTranspose.py $tmp1 > $tmp2

#cat $tmp2

tmp3=`tempfile`
cmd="joinu.py $colJoinOpts $colJoiner $tmp2 > $tmp3"
eval $cmd

#cat $tmp3

#now transpose back
matrixTranspose.py $tmp3 > $outMatrix

#now remove temp file (is this neccessary?)
rmrie.sh $tmp1
rmrie.sh $tmp2
rmrie.sh $tmp3