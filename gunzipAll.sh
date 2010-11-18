#!/bin/bash

echo all gz files are
ls *.gz

for i in *.gz; do
	echo unzipping $i
	gunzip $i;
done;

