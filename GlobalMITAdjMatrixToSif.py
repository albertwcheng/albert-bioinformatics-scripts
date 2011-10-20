#!/usr/bin/env python

from sys import *


def printUsageAndExit(programName):
	print >> stderr,programName,"MITDBNOutputFile sampleNameFile > sifFile"
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		filename,sampleNames=args
	except:
		printUsageAndExit(programName)
	
	fsn=open(sampleNames)
	sampleNames=fsn.readlines()
	fsn.close()
	for i in range(0,len(sampleNames)):
		sampleNames[i]=sampleNames[i].rstrip("\r\n")
	
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		if lino<2:
			continue #skip the first line
		thisSampleName=sampleNames[lino-2]
		adjList=lin.split(" ")
		for i in range(0,len(adjList)):
			adj=adjList[i]
			if adj=="1":
				#now connect
				print >> stdout,"%s + %s" %(thisSampleName,sampleNames[i])
	
				
	
	
	fil.close()