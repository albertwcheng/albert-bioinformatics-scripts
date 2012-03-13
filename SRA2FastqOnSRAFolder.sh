#!/bin/bash

for i in sra/*.sra; do
	echo processing $i;
	filestem=`basenameNoExt.sh $i`
	mkdir.py fastq/$filestem
	bsub fastq-dump --outdir fastq/$filestem $i
done