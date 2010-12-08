#!/usr/bin/env python

'''



Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

'''
extended bed (ebed)

1) chrom
2) chrom start g0
3) chrom end g1
4) name
5) score
6) strand
7) thickStart = CDS Start g0
8) thickEnd = CDS End g1
9) itemRGB
10) blockCount = exonCount
11) blockSizes (,)
12) blockStarts (,) relative to Chom Start in 0-based

----

genePred format

1) name
2) chrom
3) strand
4) txStart  g0
5) txEnd    g1
6) cdsStart  g0
7) cdsEnd    g1
8) exonCount  
9) exonStarts g0
10) exonEnds  g1

'''

from sys import *

''' 

these are in ebed2GenePred.py

def toStrListInPlaceRecursive(L,prefix="",suffix="",sep=",")

def ebedFields2genePredFields(fields,score,itemRgb,options)
	
def printListOfFields(stream,L,sep="\t")

'''

from ebed2GenePred import *		
	
	
if __name__=='__main__':
	from optparse import OptionParser
	
	usage="""usage: %prog  [*--genePred|--ebed] [other options] filename feature1 feature2 ...
feature list format:
transcript\ttranscription start to transcription stop of transcript
orf\ttranslation start to translation stop of transcript
5utr\t5' utr
3utr\t3' utr
cds\tcoding exons (coding regions of exons)
exon\texons
intron\tintrons
\tfor cds,exon,introns: can indicate which ones by appending an index (from 1, in transcript strand). Can change to genomic strand by specifying --genomic-index
	"""
	
	parser=OptionParser(usage)
	
	parser.add_option("--genePred",dest="inFormat",default="genePred",action="store_const",const="genePred",help="input file is genePred format. Default is genePred")
	parser.add_option("--ebed",dest="inFormat",default="genePred",action="store_const",const="ebed",help="input file is ebed format")
	parser.add_option("--fs",dest="fs",default="\t",help="set input file field separate [tab]")
	parser.add_option("--genomic-index",dest="genomicIndex",default=False,action="store_true",help="index features by genomic strand")
	
	(options,args)=parser.parse_args()
	
	try:	
		filename=args[0]
		featureList=args[1:]
	except:
		parser.print_help()
		exit()
	
	
	
	
