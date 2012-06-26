#!/usr/bin/env python

from sys import *
from getopt import getopt

def printUsageAndExit(programName):
	print >> stderr,programName," str.."



def extractAndOutputNumbers(os,S,numOfNumsToOutput):
	nums=""
	nOutputs=0
	for s in S:
		if s.isdigit():
			nums+=s
		else:
			if len(nums)>0:
				print >> os,nums
				nOutputs+=1
				if numOfNumsToOutput >0 and nOutputs>= numOfNumsToOutput:
					break
				nums=""

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['numOfNumsPerLine='])
	numOfNums=0
	
	for o,v in opts:
		if o=='--numOfNumsPerLine':
			numOfNums=int(v)
	
	#print >> stderr,numOfNums
	
	
	if len(args)==0:
		args=stdin.readlines()
	
	#print >> stderr,args
	
	for a in args:
		#print >> stderr,a
		extractAndOutputNumbers(stdout,a,numOfNums)
		
	
