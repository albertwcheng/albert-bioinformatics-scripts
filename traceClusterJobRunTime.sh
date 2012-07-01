#!/bin/bash

if [ $# -lt 2 ]; then
	echo $0 outfile sleepInt [ e.g., 5s, 10m 5hr ]
	exit 1
fi

outfile=$1
sleepInt=$2

rmrie.sh $outfile 

tpf=`tempfile`

while [ 1 ]; do
DAT=`date +%F-%T | tr ":" "-"`
echo $DAT
qstat  | awk -v TIMNOW="$DAT" 'BEGIN{firstTime=1}{match($0,/[0-9]+/,arr1); if( length(arr1[0])>0 ){match($0,/[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/,arr); tim=arr[0]; split(tim,tarr,":"); timeRan=tarr[1]*60*60+tarr[2]*60+tarr[3]; if(firstTime==1){printf("jobID\t%s\n",TIMNOW);firstTime=0} printf("%s\t%d\n", arr1[0],timeRan)}}' > $tpf #printf("%s\t%s\t%s\t%s\t%d\n", arr1[0],tarr[1],tarr[2],tarr[3],timeRan) > 

if [ ! -e $outfile ]; then
	cp $tpf $outfile
else
	mv $outfile $outfile.00
	joinu.py -fNA $outfile.00 $tpf > $outfile 2> /dev/null
	rm $outfile.00
fi

sleep $sleepInt
done