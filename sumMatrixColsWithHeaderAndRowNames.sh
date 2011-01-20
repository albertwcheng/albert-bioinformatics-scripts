#!/bin/bash

if [ $# -lt 1 ]; then
	echo $0 filename
	exit
fi



awk '{if(FNR==1){for(i=2;i<=NF;i++){headerName[i]=$i}}else{for(i=2;i<=NF;i++){sum[i]+=$i}}}END{for(i=2;i<=NF;i++){print headerName[i] "\t" sum[i]}}' $1