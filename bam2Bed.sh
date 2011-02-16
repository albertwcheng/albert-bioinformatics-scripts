#!/bin/bash

if [[ $# != 2 ]]; then
	echo $0 bamfile bedfile
	exit
fi

:<<'COMMENT'

1 QNAME String [!-?A-~]f1,255g Query template NAME


COMMENT

samtools view $bamfile | awk '($1!~/\@/ && $1!~/\#/){chrom=3; pos=$4; samFlag=$2; if(!(samFlag & 0x4)){ if(samFlag & 0x10){strand="-"}else{strand="+";}start0=pos-1; seq=$10; lseq=length(seq); end1=start0+lseq; printf("%s\t%d\t%d\t%s\n",chrom,start0,end1,strand);  }}' > bedfile