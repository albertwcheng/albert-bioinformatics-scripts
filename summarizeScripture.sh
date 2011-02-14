#!/bin/bash

if [ $# -lt 3 ]; then
	echo "$0 manifestFile SettingFile[if not found, uses \${SETTINGPATH}/\$SettingFile] runCPC[y|n] [outputDir=scriptureEbed]"
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

if [ $# -gt 3 ]; then
	outputDir=$4
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

mkdir $outputDir

for((i=0;i<$numFolders;i++)) do
	folder=${folders[$i]}
	prefix=${prefices[$i]}
	echo working on $folder with prefix $prefix
	cat $folder/*.segments > $folder/all.SEGMENTS
	addIndexToCol.py --start-row 1 --prepend $prefix. $folder/all.SEGMENTS 4 > $outputDir/$prefix.ebed
	cd $outputDir	
		mkdir.py notCoveredBy
		cd notCoveredBy
			for ncb in ${NOTCOVEREDBY[@]}; do
				ncbbn=`basename $ncb`
				#ncbbnNoExt=${ncbbn/.ebed/}
				ncbbnNoExt=`removeExt.sh $ncbbn`
				joinBedByOverlap.py ../$prefix.ebed $ncb > $prefix.coveredBy$ncbbnNoExt.ebed
				cuta.py -f4 ../$prefix.ebed | sort | uniq > allnames.00
				cuta.py -f4 $prefix.coveredBy$ncbbnNoExt.ebed | sort | uniq > coverednames.00
				subtractSets.py allnames.00 coverednames.00 > notcoverednames.00
				joinu.py -1 1 -r -2 4 notcoverednames.00 ../$prefix.ebed > $prefix.notCoveredBy$ncbbnNoExt.ebed

				#filter exon number and total length
				awk -v FS="\t" -v OFS="\t" -v blockCountLB=$blockCountLB -v totLenLB=$totLenLB '{if($10>=blockCountLB){split($11,L,","); totL=0; for(i=1;i<=length(L);i++){totL+=L[i];}if(totL>=totLenLB){print;}}}' $prefix.notCoveredBy$ncbbnNoExt.ebed > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed
				
				
				
				if [[ $runCPC == "y" ]]; then
					mkdir.py $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB
					#now make sequences
					bedSeq $genomeSeq $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed ebed > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq
					bedSeqColN=`colNum.sh $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq`
					reverseComplement.py $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq $bedSeqColN > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq.rev
					awk -v FS="\t" '{printf(">%s\n%s\n",$4,$13);printf(">%s(revcomp)\n%s\n",$4,$14);}'  $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq.rev > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq.rev.fasta
				
					CPCStepOne.sh $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebedseq.rev.fasta $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB/CPC $splitsCPCSeq
				
				fi
				
				
				#awk -v FS="\t" -v OFS="\t" '$1!="chrM"' $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.notChrM.ebed
			done
		cd ..
	cd ..
done