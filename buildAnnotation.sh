#!/bin/bash

if [ $# -lt 4 ]; then
	echo "$0 friendlyName outputDir setting [ [listOFBeds(ending in list)OrBedFiles] ... ]"
	echo "\${SETTINGPATH}=${SETTINGPATH}"
	if [[ ${SETTINGPATH} != "" ]]; then
		if [ -e ${SETTINGPATH} ]; then
			echo ""
			echo "setting files available in setting path are:"
			ls ${SETTINGPATH}/*.shvar
			echo "list files available in setting path are:"
			ls ${SETTINGPATH}/*.list
		fi
	fi
	exit
fi

friendlyName=$1
outputDir=$2
settingFile=$3

outputDir=`abspath.py $outputDir`

if [ -e $settingFile ]; then
	source $settingFile
else
	if [ -e ./$settingFile ]; then
		source ./$settingFile
	else
		if [ -e $SETTINGPATH/$settingFile ]; then
			echo "using $SETTINGPATH/$filename"
			source $SETTINGPATH/$settingFile
		else
			echo "$settingFile not found. Not in current dir not in \$SETTINGPATH=$SETTINGPATH"
			exit
		fi
	fi
fi


if [ -e $outputDir ]; then
	rm -R $outputDir
fi

mkdir.py $outputDir

shift
shift
shift

while [ $# -gt 0 ]; do

filename=$1
extension=`getExt.sh $filename`

if [[ $extension == "list" ]]; then

	if [ -e $filename ]; then
		filenames=(`cat $filename`)
	else
		if [ -e ./$filename ]; then
			filenames=(`cat ./$filename`)
		else
			if [ -e $SETTINGPATH/$filename ]; then
				echo "using $SETTINGPATH/$filename"
				filenames=(`cat $SETTINGPATH/$filename`)
			else
				echo "$filename not found. Not in current dir not in \$SETTINGPATH=$SETTINGPATH"
				exit
			fi
		fi
	fi
	
	echo "loading bed file listed in $filename"
	
	for filename in ${filenames[@]}; do
		echo -e "\tadding bed file $filename"
		cat $filename >> $outputDir/combined.ebed
	done
	
else
	echo "adding bed file $filename"
	cat $filename >> $outputDir/combined.ebed
fi	

shift

done

#now easyCluster
echo "easy cluster on combined.ebed"
easyClusterGenesOnEbed.py --not-append-filename-to-combined-name --transcript-exon-number-lower-bound $transcriptExonNumberLowerBound --splice-site-align-lower-bound $spliceSiteAlignLowerBound $strandwareFlag --use-friendly-name $friendlyName $forceNumberOfDigits $outputDir/combined.friendlymap --randomize-color --add-header $friendlyName "$friendlyName Track" itemRgb/On+visibility/full $outputDir/combined.ebed > $outputDir/combined.clustered.ebed
#strandwareFlag=--strand-aware
#spliceSiteAlignLowerBound=1
#transcriptExonNumberLowerBound=0
#forceNumberOfDigits=8
