#!/usr/bin/env python

from sys import *
from optparse import OptionParser

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
'''

def printUsageAndExit(parser):
	parser.print_help()
	exit(1)

if __name__=='__main__':
	
	chroms=dict()
	nameOrder=[]
	entries=dict()
	
	parser=OptionParser(usage="Usage: %prog [Options] inbed")
	parser.add_option("--default-score",dest="defaultScore",default="0",help="Use this as score if not provided [0]")
	parser.add_option("--default-strand",dest="defaultStrand",default=".",help="Use this as strand if not provided [.]")
	parser.add_option("--fs",dest="FS",default="\t",help="set fields separator [tab]")
	(options, args) = parser.parse_args()
	
	try:
		filename,=args
	except:
		printUsageAndExit(parser)
	
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=="#":
			#comment or no content line, just print
			print >> stdout,lin
		else:
			fields=lin.split(options.FS)
			if len(fields)>6:
				print >> stderr,"warning: more than 6 fields. The extra fields are ignored"
			
			if len(fields)<4:
				print >> stderr,"no name available for this entry. abort"
				exit(1)
			
			
	
				
	
	