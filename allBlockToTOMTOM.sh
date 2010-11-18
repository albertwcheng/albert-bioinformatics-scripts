#!/bin/bash

origPath=`pwd`
cd ..


python $origPath/extractBlockFromMemeOutput.py
#now we have block files

#now convert block to fa's and tomtom's
for i in *.block; do
	bash $origPath/blocks2Fa.sh $i ${i/.block/.fa}
	python $origPath/motifAlignment2TOMTOM.py ${i/.block/.fa} > ${i/.block/.tomtom}

done;

cd $origPath
