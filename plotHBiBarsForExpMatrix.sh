#!/bin/bash

if [ $# -lt 6 ]; then
	echo $0 matrix geneCol leftCol rightCol outdir prefix
	exit 1
fi

matrix=$1
gene=$2
left=$3
right=$4
outdir=$5
prefix=$6

if [ ! -e $outdir ]; then
	mkdir.py $outdir
fi

geneCol=`colSelect.py $matrix $gene`
leftCol=`colSelect.py $matrix $left`
rightCol=`colSelect.py $matrix $right`

awk -v FS="\t" -v OFS="\t" -v geneCol=$geneCol -v leftCol=$leftCol -v rightCol=$rightCol '{if(FNR>1){printf("%s\t%f\n",$geneCol,$leftCol-$rightCol);}}' $matrix | sort -k2,2 -g -r > $outdir/$prefix.matrix.diff.sorted.noheader

echo -e "GeneName\tDiff" > $outdir/$prefix.matrix.diff.sorted.txt
cat $outdir/$prefix.matrix.diff.sorted.noheader >>  $outdir/$prefix.matrix.diff.sorted.txt

matrixToCDT.sh  $outdir/$prefix.matrix.diff.sorted.txt $outdir/$prefix.matrix.diff.sorted.cdt

plotColorMap.py --color-map RdYlGn_r $outdir/$prefix.matrix.diff.sorted.txt $outdir/$prefix.matrix.diff.sorted.heatmap.pdf

echo -e "GeneName\tNegative\tPositive" > $outdir/$prefix.matrix.diff.3cols.sorted.txt
#now make the three column file
awk -v FS="\t" -v OFS="\t" '{v2="NA";v3="NA";if($2>0){v3=$2}else{v2=$2} printf("%s\t%s\t%s\n",$1,v2,v3);}' $outdir/$prefix.matrix.diff.sorted.noheader >> $outdir/$prefix.matrix.diff.3cols.sorted.txt




#now plot
#plotHBiBars.py  --XLabel log2fc --font-size 8 --left-annot-col .GeneName --right-annot-col .GeneName $outdir/$prefix.matrix.diff.3cols.sorted.txt .Negative .Positive $outdir/$prefix.plot.pdf 

plotHBiBars.py --left-face-color green --right-face-color red --XLabel log2fc --font-size 8  $outdir/$prefix.matrix.diff.3cols.sorted.txt .Negative .Positive $outdir/$prefix.plot.offLabel.pdf 

plotHBiBars.py --left-face-color green --right-face-color red --left-annot-col .GeneName --right-annot-col .GeneName --left-annot-only Npas4,Fos,Arc --right-annot-only Npas4,Fos,Arc --XLabel log2fc --font-size 8  $outdir/$prefix.matrix.diff.3cols.sorted.txt .Negative .Positive $outdir/$prefix.plot.offLabelWithGeneLabelled.pdf 

#plotHBiBars.py --annot-col .GeneName --annot-only Npas4,Fos,Arc --left-face-color green --right-face-color red --single-col-mode --XLabel log2fc --font-size 8  $outdir/$prefix.matrix.diff.sorted.txt .Diff $outdir/$prefix.plot.offLabel2.pdf 