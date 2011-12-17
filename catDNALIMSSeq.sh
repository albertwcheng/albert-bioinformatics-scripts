#!/bin/bash

### cat the DNA lims seq together and output to a name either automatically using the common prefix or using a name

if [ $# -lt 1 ]; then
	echo $0 "[ output file non-existent ] in1 in2 .... in3"
	echo if output file exists, then an automatic name will be generated using the common prefix of the basenames of the seq files
	exit 1
fi

firstFile=$1

ind=0

outName=""

if [ -e $firstFile ]; then
	ins[$ind]=$firstFile
	ind=`expr $ind + 1`
else
	outName=$firstFile
fi

shift

while [ $# -ge 1 ]; do
	#echo $1
	ins[$ind]=$1
	ind=`expr $ind + 1`
	shift
done



if [[ $outName == "" ]]; then
	#derive common prefix
	outName=`commonPrefix.py ${ins[@]}`
	
fi

echo the outName is $outName
echo extension .txt
echo the input files are
for fil in ${ins[@]}; do
	echo $fil
done

if [ -e $outName ]; then
	echo $outName existed. Abort
	exit 1
fi

if [[ $outName == "" ]]; then
	echo output filename invalid. Abort
	exit 1
fi

#now go to files

for fil in ${ins[@]}; do
	cat $fil >> $outName.txt
	echo "" >> $outName.txt
done