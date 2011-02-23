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
	
	if len(intervals)==0:
		print >> stderr,"no intervals provided"
		raise ValueError
		
	chrom=intervals[0][0]
	#first pass:add all coords into blockBounds
	for interval in intervals:
		tchrom,start0,end1=interval[:3]
		if tchrom!=chrom:
			print >> stderr,"inconsistent chromosomes. was",chrom,"now",tchrom
			raise ValueError
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
			raise ValueError
			
		try:
			eI=blockBounds.index(end1)
		except:
			print >> stderr,"error end1=",end1,"not indexed"
			print >> stderr,"blockBounds=",blockBounds
			raise ValueError
		
		for i in range(sI,eI):
			blockCounts[i]+=1
		
	return chrom,blockBounds,blockCounts


def toStrArray(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL

def printUsageAndExit(programName):
	print >> stderr,"Usage",programName,"[options] inbed"
	print >> stderr,"from a bed file of chr start0 end1, find regions that are represented at least a number of times"
	print >> stderr,"Options:"
	print >> stderr,"--block-count-min [default:1]. set block count min threshold to be retained in output"
	print >> stderr,"--append-count. append a column of block count"
	print >> stderr,"--out-one-line. output as one line transcript bed entry"
	print >> stderr,"--ool-strand [default:.]. set strand for one line output"
	print >> stderr,"--ool-name [default:.]. set name for one line output"
	print >> stderr,"--ool-score [default: 0]. set score for one line output"
	print >> stderr,"--ool-itemRgb [defualt: 0,0,0]. set itemRgb for one line output"
	exit()

if __name__=='__main__':
	#intervals=[ ('chr1',0,21), ('chr1',10,30), ('chr1',20,25) , ('chr1',50,100)]
	#print getNonOverlappingBlocks(intervals)
	programName=argv[0]
	blockCountMin=1
	appendCount=False
	onelineBedOut=False
	oolscore='0'
	oolname='.'
	oolstrand='.'
	oolitemrgb="0,0,0"
	opts,args=getopt(argv[1:],'',['block-count-min=','append-count','out-one-line','ool-score=','ool-name=','ool-strand=','ool-itemRgb='])
	for o,v in opts:
		if o=='--block-count-min':
			blockCountMin=int(v)
		elif o=='--append-count':
			appendCount=True
		elif o=='--out-one-line':
			onelineBedOut=True
		elif o=='--ool-score':
			oolscore=v
		elif o=='--ool-name':
			oolname=v
		elif o=='--ool-strand':
			oolstrand=v	
		elif o=='--ool-itemRgb':
			oolitemrgb=v
			
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
	
	oneLineStarts0=[]
	oneLineLengths=[]
	
	lastBlockEnd1=-1
	firstBlockStart0=-1
	
	for i in range(0,len(blockCounts)):
		blockStart0=blockBounds[i]
		blockEnd1=blockBounds[i+1]
		blockCount=blockCounts[i]
		if blockCount>=blockCountMin:
			#output!
			if onelineBedOut:
				if firstBlockStart0==-1:
					firstBlockStart0=blockStart0
				lastBlockEnd1=blockEnd1
				
				oneLineStarts0.append(blockStart0-firstBlockStart0)
				oneLineLengths.append(blockEnd1-blockStart0)
				
			else:
				outputV=[chrom,str(blockStart0),str(blockEnd1)]
				if appendCount:
					outputV.append(str(blockCount))
				
				print >> stdout,"\t".join(outputV)
				
	
	if onelineBedOut and len(oneLineStarts0)>0:
		oneLineStarts0=toStrArray(oneLineStarts0)
		oneLineLengths=toStrArray(oneLineLengths)
		outputV=[chrom,str(firstBlockStart0),str(lastBlockEnd1),oolname,oolscore,oolstrand,str(firstBlockStart0),str(lastBlockEnd1),str(oolitemrgb),str(len(oneLineStarts0)),",".join(oneLineLengths),",".join(oneLineStarts0)]
		print >> stdout,"\t".join(outputV)
		