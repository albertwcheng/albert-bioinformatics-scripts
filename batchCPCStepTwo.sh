#!/bin/bash

if [ $# -lt 2 ]; then
	echo "$0 manifestFile SettingFile[if not found, uses \${SETTINGPATH}/\$SettingFile] [scriptureEbedDir=scriptureEbed]"
	echo "\${SETTINGPATH}=${SETTINGPATH}"
	if [[ ${SETTINGPATH} != "" ]]; then
		if [ -e ${SETTINGPATH} ]; then
			echo ""
			echo "setting files available in path are:"
			ls ${SETTINGPATH}
		fi
	fi
	echo ""
	echo make a manifest file containing the folder name and the renaming of the transcripts
	echo e.g.,
	echo Mmu_Oocyte	Mmu.Oocyte.GSE14605
	echo Mmu_DicerKO_Oocyte	Mmu.DicerKOOocyte.GSE14605
	echo Mmu_AgoKO_Oocyte	Mmu.AgoKOOocyte.GSE14605
	echo Mmu_4_cell_blastomere	Mmu.4cellblastomere.GSE1460
	exit
fi

if [ $# -gt 2 ]; then
	outputDir=$3
else
	outputDir=scriptureEbed
fi

manifestFile=$1
settingFile=$2
runCPC=$3


if [ -e $settingFile ]; then
	source $settingFile
else
	if [ -e ./$settingFile ]; then
		source ./$settingFile
	else
		if [ -e $SETTINGPATH/$settingFile ]; then
			echo "using $SETTINGPATH/$settingFile"
			source $SETTINGPATH/$settingFile
		else
			echo "$settingFile not found. Not in current dir not in \$SETTINGPATH=$SETTINGPATH"
			exit
		fi
	fi
fi

:<<'COMMENT'
manifest.txt:
setting.shvar

folder[\t]transcriptRenamePrefix

e.g.,

Mmu_Oocyte	Mmu.Oocyte.GSE14605
Mmu_DicerKO_Oocyte	Mmu.DicerKOOocyte.GSE14605
Mmu_AgoKO_Oocyte	Mmu.AgoKOOocyte.GSE14605
Mmu_4_cell_blastomere	Mmu.4cellblastomere.GSE14605

COMMENT



folders=(`cuta.py -f1 $manifestFile`)
prefices=(`cuta.py -f2 $manifestFile`)

numFolders=${#folders[@]}
numPrefices=${#prefices[@]}

if [[ $numFolders != $numPrefices ]]; then
	echo "unequal number of folders and prefices specified. abort"
	exit
fi

echo $numFolders of folders specified [ ${folders[@]} ]
echo $numPrefices of prefices specified [ ${prefices[@]} ]



for((i=0;i<$numFolders;i++)) do
	folder=${folders[$i]}
	prefix=${prefices[$i]}
	echo working on $folder with prefix $prefix
	
	cd $outputDir	
		
		cd notCoveredBy
			for ncb in ${NOTCOVEREDBY[@]}; do
				ncbbn=`basename $ncb`
				#ncbbnNoExt=${ncbbn/.ebed/}
				ncbbnNoExt=`removeExt.sh $ncbbn`
				
				bedpath=$prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed
				cpcpath=$prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB/CPC
				cpcsummarypath=$prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB/CPCSummary
				
				bsub CPCStepTwoSummarize.sh $cpcpath $cpcsummarypath -1 $bedpath
				
			done
		cd ..
	cd ..
done