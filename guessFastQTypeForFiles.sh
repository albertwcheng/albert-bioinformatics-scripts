#!/bin/bash

if [ $# -lt 1 ]; then
	echo Usage: $0 file1 file2 ....
	exit
fi

numFiles=$#

echo "received $numFiles number of files"

guessFileReturn[0]=""
origFileName[0]=""

while(($#>=1)); do
	fileToCheck=$1
	shift
	bsub "guessFastQType.py $fileToCheck > $fileToCheck.guess" #| qsub -d `pwd` #2> $fileToCheck.guess.stderr
	#guessFileReturn[${#guessFileReturn[@]}]=$fileToCheck.guess.00
	#origFileName[${#origFileName[@]}]=$fileToCheck
	#echo -e "$fileToCheck\t$guess"
	#echo $fileToCheck
done

exit

echo "job submitted. Now wait for return"

jobAllFinished=1


while((1));do
	sleep 120
	#now check if ready
	for((i=1;i<${#guessFileReturn[@]};i++)); do
		thisReturn=${guessFileReturn[$i]}
		#echo $thisReturn
		if [ -e $thisReturn ]; then   #file exists?
			wcl=`wc -l $thisReturn | cut -d" " -f1`
			if(($wcl==0)); then
				jobAllFinished=0
				break
			fi
		else
			#not even exists
			jobAllFinished=0
			break
		fi
	done
	
	if((jobAllFinished)); then
		break
	fi
done


#now merge #start from 1
for((i=1;i<${#guessFileReturn[@]};i++));
	thisReturn=${guessFileReturn[$i]}
	thisOrigFile=${origFileName[$i]}
	guess=`cat $thisReturn`
	echo -e "$thisOrigFile\t$guess"
done	
