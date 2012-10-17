#!/bin/bash

for i in *.seq; do
	seqName=${i/.seq/};
	seqNameRenamed=`pyeval.py "'$seqName'.split('-')[1].replace('s','-')+'_'+'$seqName'.split('-')[2].split('_')[0]"`
	echo $seqName $seqNameRenamed
	echo ">$seqNameRenamed" > $seqNameRenamed.fa
	cat $i >> $seqNameRenamed.fa
done

cat *.fa > merged.FASTA