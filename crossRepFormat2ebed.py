#!/usr/bin/env python

from sys import *

def printUsageAndExit(programName):
	print >> stderr,programName,"crossRepIn > outEbed"
	exit(1)
	

def fromCrossesToEbedStruct(cross):
	gStart=-1
	eStart=-1
	
	blockStarts0=[]
	blockSizes=[]
	
	for i in range(0,len(cross)):
		if cross[i] in ['>','<','x']:
			if gStart==-1:
				gStart=i
			if eStart==-1:
				eStart=i-gStart
		else:
			if eStart>=0:
				blockStarts0.append(eStart)
				blockSizes.append(i-eStart-gStart)
				eStart=-1
	
	if eStart>=0:
		blockStarts0.append(eStart)
		blockSizes.append(len(cross)-eStart-gStart)
	
	gend1=blockSizes[-1]+blockStarts0[-1]+gStart
	
	return gStart,gend1,blockStarts0,blockSizes	

def toStrList(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	
	return sL


if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
		
		
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)==0 or lin[0]=="#":
			continue
		
		name,chrom,cross=lin.split(",")
		
		
		if '>' in cross:
			strand="+"
		elif '<' in cross:
			strand="-"
		else:
			strand="."
		
		gstart0,gend1,blockStarts,blockSizes=fromCrossesToEbedStruct(cross)
		
		blockCount=len(blockStarts)
		
		blockStarts=",".join(toStrList(blockStarts))
		blockSizes=",".join(toStrList(blockSizes))
	
		print >> stdout,"\t".join(toStrList((chrom,gstart0,gend1,name,0,strand,gstart0,gend1,"0,0,0",blockCount,blockSizes,blockStarts)))
		
		
	fil.close()