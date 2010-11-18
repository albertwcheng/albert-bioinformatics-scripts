#!/bin/bash

if [ $# -lt 5 ]; then
	echo $0 geneList aceviewProteinFastaRoot smartResultDatabaseRoot checkExists [ 1 or 0 ] tmpRoot [ . ]
	exit
fi

geneList=$1
aceviewProteinFastaRoot=$2
smartResultDatabaseRoot=$3
checkExists=$4
tmpRoot=$5

#now load gene list
genes=( `cat $geneList` )
ngenesLoaded=${#genes[@]}
echo $ngenesLoaded number of genes loaded


tmpfolder=$tmpRoot/tmp
if [ ! -e $tmpfolder ]; then
	mkdir $tmpfolder
fi

if [[ $checkExists == 1 ]]; then
	#save time not to redo the existing ones
	rm $tmpfolder/genesToGetThisTime.txt
	for gene in ${genes[@]}; do
		if [ -e $smartResultDatabaseRoot/${gene}.*_SMART_results.txt ]; then
			echo ${gene} existed in database, ignored
		else
			echo ${gene} >> $tmpfolder/genesToGetThisTime.txt
		fi
	done
		
else
	cp $geneList $tmpfolder/genesToGetThisTime.txt
fi

genesToGet=( `cat $tmpfolder/genesToGetThisTime.txt` )
ngenesToGet=${#genesToGet[@]}
echo $ngenesToGet number of genes to get from SMART

#now join sequences on names

seqfile=$aceviewProteinFastaRoot/allGoodProtein.oneline.addedM.SEQ.geneNameAppended

joinu.py -w 2 $tmpfolder/genesToGetThisTime.txt $seqfile > $tmpfolder/genesToGetThisTime.SEQ.geneNameAppended

#now get back SEQ

cuta.py -f2,3 $tmpfolder/genesToGetThisTime.SEQ.geneNameAppended > $tmpfolder/genesToGetThisTime.SEQ

#now get back FASTA

seq2fasta.sh $tmpfolder/genesToGetThisTime.SEQ  $tmpfolder/genesToGetThisTime.fasta

#now split into chucks of job

rm -R $tmpfolder/chunks
mkdir $tmpfolder/chunks

split -l 1000 $tmpfolder/genesToGetThisTime.fasta $tmpfolder/chunks/geneToGetThisTimeChunk.

cd $tmpfolder/chunks/

for chunkjob in geneToGetThisTimeChunk.*; do
	bsub SMART_batch.pl --inputFile ${chunkjob} --outputDirectory $smartResultDatabaseRoot --includePfam --includeSignalP --includeRepeats --includeDISEMBL
done

