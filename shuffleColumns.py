#!/usr/bin/env python

from albertcommon import *
from getopt import getopt
from sys import *

def printUsageAndExit(programName):
	print >> stderr,programName,"infile targetColumns Trials targetFileName[e.g., shuffled_%d ] for shuffled_1 shuffled_2 ..."
	explainColumns(stderr)
	exit(1)

def arrangeVector(src,fro,to):
	dst=src[:]
	for f,t in zip(fro,to):
		dst[t]=src[f]
	
	return dst


if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',[])
	
	try:
		infile,targetColumns,Trials,targetFileName=args
	except:
		printUsageAndExit(programName)
		
		
	startRow=2
	headerRow=1
	fs="\t"
	Trials=int(Trials)
	
	header,prestarts=getHeader(infile,headerRow,startRow,fs)
	shuffleTargets=getCol0ListFromCol1ListStringAdv(header,targetColumns)
	shuffleTo=shuffleTargets[:]
	history=set()
	
	randomShuffleNoRepeat(shuffleTo,history)
	
	NT=0
	while randomShuffleNoRepeat(shuffleTo,history):
		NT+=1
		
		
		TfileName=targetFileName %(NT)
		print >> stderr,"Generating trial %d as %s" %(NT,TfileName)
		
		fil=open(infile)
		fout=open(TfileName,"w")
		lino=0
		for lin in fil:
			fields=lin.rstrip("\r\n").split(fs)
			afields=arrangeVector(fields,shuffleTargets,shuffleTo)
			print >> fout,fs.join(afields)
		
		fil.close()
		fout.close()

		if NT>=Trials:
			break