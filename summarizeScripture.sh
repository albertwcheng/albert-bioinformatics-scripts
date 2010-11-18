#!/bin/bash

source setting.shvar
:<<'COMMENT'
manifest.txt:
setting.shvar

folder[\t]transcriptRenamePrefix

e.g.,

Mmu_Oocyte	Mmu.Oocyte.GSE14605.
Mmu_DicerKO_Oocyte	Mmu.DicerKOOocyte.GSE14605.
Mmu_AgoKO_Oocyte	Mmu.AgoKOOocyte.GSE14605.
Mmu_4_cell_blastomere	Mmu.4cellblastomere.GSE14605.

COMMENT

if [ ! -e manifest.txt ]; then
	echo make a manifest.txt file containing the folder name and the renaming of the transcripts
	echo e.g.,
	echo Mmu_Oocyte	Mmu.Oocyte.GSE14605.
	echo Mmu_DicerKO_Oocyte	Mmu.DicerKOOocyte.GSE14605.
	echo Mmu_AgoKO_Oocyte	Mmu.AgoKOOocyte.GSE14605.
	echo Mmu_4_cell_blastomere	Mmu.4cellblastomere.GSE14605
	exit
fi

folders=(`cuta.py -f1 manifest.txt`)
prefices=(`cuta.py -f2 manifest.txt`)

numFolders=${#folders[@]}
numPrefices=${#prefices[@]}

if [[ $numFolders != $numPrefices ]]; then
	echo "unequal number of folders and prefices specified. abort"
	exit
fi

echo $numFolders of folders specified [ ${folders[@]} ]
echo $numPrefices of prefices specified [ ${prefices[@]} ]

mkdir scriptureEbed

for((i=0;i<$numFolders;i++)) do
	folder=${folders[$i]}
	prefix=${prefices[$i]}
	echo working on $folder with prefix $prefix
	cat $folder/*.segments > $folder/all.SEGMENTS
	addIndexToCol.py --start-row 1 --prepend $prefix $folder/all.SEGMENTS 4 > scriptureEbed/$prefix.ebed
	cd scriptureEbed	
		mkdir notCoveredBy
		cd notCoveredBy
			for ncb in ${NOTCOVEREDBY[@]}; do
				ncbbn=`basename $ncb`
				ncbbnNoExt=${ncbbn/.ebed/}
				joinBedByOverlap.py ../$prefix.ebed $ncb > $prefix.coveredBy$ncbbnNoExt.ebed
				cuta.py -f4 ../$prefix.ebed | sort | uniq > allnames.00
				cuta.py -f4 $prefix.coveredBy$ncbbnNoExt.ebed | sort | uniq > coverednames.00
				subtractSets.py allnames.00 coverednames.00 > notcoverednames.00
				joinu.py -1 1 -r -2 4 notcoverednames.00 ../$prefix.ebed > $prefix.notCoveredBy$ncbbnNoExt.ebed
				blockCountLB=2
				totLenLB=200
				#filter exon number and total length
				awk -v FS="\t" -v OFS="\t" -v blockCountLB=$blockCountLB -v totLenLB=$totLenLB '{if($10>=blockCountLB){split($11,L,","); totL=0; for(i=1;i<=length(L);i++){totL+=L[i];}if(totL>=totLenLB){print;}}}' $prefix.notCoveredBy$ncbbnNoExt.ebed > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed
				awk -v FS="\t" -v OFS="\t" '$1!="chrM"' $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.ebed > $prefix.notCoveredBy$ncbbnNoExt.exonCountGe$blockCountLB.totLenGe$totLenLB.notChrM.ebed
			done
		cd ..
	cd ..
done