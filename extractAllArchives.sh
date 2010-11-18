#!/bin/bash



for i in *.tar.gz; do
	echo "extracting $i"
	tar -xvf $i;
done

for i in *.tgz; do
	echo "extracting $i"
	tar -xvf $i;
done

for i in *.tar.bz2; do
	echo "extracting $i"
	tar -jxvf $i;
done

for i in *.gz; do
	echo "unzipping $i"
	gunzip $i
done

for i in *.bz2; do
	echo "unzipping $i"
	bunzip2 $i;
done
	 
