#!/bin/bash

echo please use bamtools convert --format bed -in <bamfile> -out <bedfile> for conversion instead
exit

if [[ $# != 2 ]]; then
	echo $0 bamfile bedfile
	exit
fi

:<<'COMMENT'

1 QNAME String [!-?A-~]f1,255g Query template NAME2 FLAG Int [0,216-1] bitwise FLAG3 RNAME String \*|[!-()+-<>-~][!-~]* Reference sequence NAME4 POS Int [0,229-1] 1-based leftmost mapping POSition5 MAPQ Int [0,28-1] MAPping Quality6 CIGAR String \*|([0-9]+[MIDNSHPX=])+ CIGAR string7 RNEXT String \*|=|[!-()+-<>-~][!-~]* Ref. name of the mate/next fragment8 PNEXT Int [0,229-1] Position of the mate/next fragment9 TLEN Int [-229+1,229-1] observed Template LENgth10 SEQ String \*|[A-Za-z=.]+ fragment SEQuence11 QUAL String [!-~]+ ASCII of Phred-scaled base QUALity+33


COMMENT

bamfile=$1
bedfile=$2

samtools view $bamfile | awk '($1!~/\@/ && $1!~/\#/){chrom=3; pos=$4; samFlag=$2; if(!( and(samFlag,0x4))){ if(and(samFlag,0x10)){strand="-"}else{strand="+";}start0=pos-1; seq=$10; lseq=length(seq); end1=start0+lseq; printf("%s\t%d\t%d\t%s\n",chrom,start0,end1,strand);  }}' > bedfile