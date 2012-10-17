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
	
	print >> stderr,"this is potentially buggy??"
	exit(1)
	
	chroms=dict()
	nameOrder=[]
	entries=dict()

	parser=OptionParser(usage="Usage: %prog [Options] inbed")
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
			#if len(fields)>6:
			#	print >> stderr,"warning: more than 6 fields. The extra fields are ignored"

			if len(fields)<4:
				print >> stderr,"no name available for this entry. abort"
				exit(1)
	
	
			name=fields[3]
			chrom=fields[0]
			gstart0=int(fields[1])
			gend1=int(fields[2])
			
			if name not in nameOrder:
				nameOrder.append(name)
				entries[name]=[chrom,gstart0,gend1]
			else:
				ent_chrom,ent_gstart0,ent_gend1=entries[name]
				if ent_chrom!=chrom:
					print >> stderr,"warning and removed: chrom not consistent for entry",fields,"was",entries[name]
					entries[name][0]="Error"
					
				ent_gstart0=min(gstart0,ent_gstart0)
				ent_gend1=max(gend1,ent_gend1) #was min???
				entries[name][1]=ent_gstart0
				entries[name][2]=ent_gend1
				
	
	fil.close()
	
	for name in nameOrder:
		chrom,gstart0,gend1=entries[name]
		if chrom=="Error":
			continue
		print >> stdout,chrom+"\t"+str(gstart0)+"\t"+str(gend1)+"\t"+"_".join(name.split())
		
	
				
			