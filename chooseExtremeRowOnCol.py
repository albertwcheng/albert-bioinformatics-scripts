#!/usr/bin/env python

from albertcommon import *

def printUsageAndExit(programName):
	print >> stderr,"Usage: %s filename keycols criteriaCol <min|max>" %(programName)
	exit(1)

selFuncs=dict()

def smaller(record,new):
	return new<record

def larger(record,new):
	return new>record

selFuncs["min"]=smaller
selFuncs["max"]=larger

if __name__='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,keycols,criteriaCol,selectorFunc=args
	except:
		printUsageAndExit(programName)
	
	fs="\t"
	startRow=2
	headerRow=1
	#headerRow-=1
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
		
	keycols=getCol0ListFromCol1ListStringAdv(header,keycols)
	criteriaCol=getCol0ListFromCol1ListStringAdv(header,criteriaCol)[0]
	
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue
			
		getSubvector(keycols)
	
	fil.close()