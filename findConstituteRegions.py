#!/usr/bin/env python


from sys import *
from getopt import getopt

def zeros(n):
	L=[]
	for i in range(0,n):
		L.append(0)
	return L

#intervals=[ (chr,start0,end1),....]
#returns chr, blockBounds, blockCounts
#where blockBounds = [ b1,b2,b3,b4,b5 ]. blocks (start0,end1) are (b1,b2),(b2,b3),...,(b4,b5)
#where blockCounts = [c1,c2,c3,c4] where c1 is for (b1,b2), c2 is for (b2,b3), etc

def getNonOverlappingBlocks(intervals):
	blockBounds=set()
	
	chrom=""
	
	#first pass:add all coords into blockBounds
	for interval in intervals:
		chrom,start0,end1=interval[:3]
		blockBounds.add(start0)
		blockBounds.add(end1)
	
	#now convert blockBounds into list and sort
	blockBounds=list(blockBounds)
	blockBounds.sort()
	
	nBlocks=len(blockBounds)-1
	
	blockCounts=zeros(nBlocks)
	
	#second pass: go to each interval and count
	for interval in intervals:
		chrom,start0,end1=interval[:3]
		try:
			sI=blockBounds.index(start0)
		except:
			print >> stderr,"error start0=",start0,"not indexed"
			print >> stderr,"blockBounds=",blockBounds
			exit()
		try:
			eI=blockBounds.index(end1)
		except:
			print >> stderr,"error end1=",end1,"not indexed"
			print >> stderr,"blockBounds=",blockBounds
			exit()
		
		for i in range(sI,eI):
			blockCounts[i]+=1
		
	return chrom,blockBounds,blockCounts


def printUsageAndExit(programName):
	print >> stderr,"Usage",programName,"[options] inbed"
	print >> stderr,"from a bed file of chr start0 end1, find regions that are represented at least a number of times"
	print >> stderr,"Options:"
	print >> stderr,"--block-count-min [default:1]. set block count min threshold to be retained in output"
	print >> stderr,"--append-count. append a column of block count"
	exit()

if __name__=='__main__':
	#intervals=[ ('chr1',0,21), ('chr1',10,30), ('chr1',20,25) , ('chr1',50,100)]
	#print getNonOverlappingBlocks(intervals)
	programName=argv[0]
	blockCountMin=1
	appendCount=False
	opts,args=getopt(argv[1:],'',['--block-count-min=','append-count'])
	for o,v in opts:
		if o=='--block-count-min':
			blockCountMin=int(v)
		elif o=='--append-count':
			appendCount=True
			
	try:
		inbed,=args
	except:
		printUsageAndExit(programName)
	
	intervals=[]
	fil=open(inbed)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=='#':
			continue
		fields=lin.split("\t")
		try:
			chrom,start0,end1=fields[:3]
			interval=(chrom,int(start0),int(end1))
			intervals.append(interval)
		except:
			print >> stderr,"invalid line",lino,"ignored:",fields
			continue
		
	fil.close()
	#now getNonOverlappingBlocks
	
	chrom,blockBounds,blockCounts=getNonOverlappingBlocks(intervals)
	for i in range(0,len(blockCounts)):
		blockStart0=blockBounds[i]
		blockEnd1=blockBounds[i+1]
		blockCount=blockCounts[i]
		if blockCount>=blockCountMin:
			#output!
			outputV=[chrom,str(blockStart0),str(blockEnd1)]
			if appendCount:
				outputV.append(str(blockCount))
			
			print >> stdout,"\t".join(outputV)