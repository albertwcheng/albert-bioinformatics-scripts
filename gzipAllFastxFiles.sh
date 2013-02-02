#!/bin/bash

for i in *.fastq; do
	if [ -e $i ]; then
		bsub -e /dev/null -o /dev/null gzip $i
	fi
done

for i in *.fasta; do
	if [ -e $i ]; then
		bsub -e /dev/null -o /dev/null gzip $i
	fi
done
