#!/usr/bin/env python

from sys import *
from optparse import OptionParser
from operator import *
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

def toStrList(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL	

if __name__=='__main__':

	chroms=dict()
	#nameOrder=[]
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
			
			try:
				strand=fields[5]
			except:
				strand="."
			
			try:
				ent_chrom,ent_gstart0,ent_gend1,strand,blocks=entries[name]
				if ent_chrom!=chrom:
					print >> stderr,"warning and removed: chrom not consistent for entry",fields,"was",entries[name]
					entries[name][0]="Error"
					
				entries[name][1]=min(gstart0,ent_gstart0)
				entries[name][2]=max(gend1,ent_gend1)					
			except:
				entries[name]=[chrom,gstart0,gend1,strand,[]]				
				ent_chrom,ent_gstart0,ent_gend1,strand,blocks=entries[name]
			

				
			blocks.append((gstart0,gend1))
				
	
	fil.close()
	
	for name,entry in entries.items():
		chrom,gstart0,gend1,strand,blocks=entry
		if chrom=="Error":
			continue
		#print >> stdout,chrom+"\t"+str(gstart0)+"\t"+str(gend1)+"\t"+"_".join(name.split())
		
		score=0
		thickStart=gstart0
		thickEnd=gend1
		itemRGB="0,0,0"
		blockCount=len(blocks)
		blocks.sort(key=itemgetter(0))
		blockSizes=[]
		blockStarts=[]
		for block in blocks:
			blockSizes.append(block[1]-block[0])
			blockStarts.append(block[0]-gstart0)
		
		print >> stdout,"\t".join(toStrList([chrom,gstart0,gend1,name,score,strand,thickStart,thickEnd,itemRGB,blockCount,",".join(toStrList(blockSizes)),",".join(toStrList(blockStarts))]))
		
				
			