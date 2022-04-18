#!/usr/bin/env python2.7

from sys import *
from getopt import getopt

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] inGenBank > outSeq"
	print >> stderr,"Options:"
	print >> stderr,"--out-seq [default]"
	print >> stderr,"--out-fasta"
	exit(1)

def hasPrefix(haystack,needle):
	if len(haystack)<len(needle):
		return False
	
	return haystack[0:len(needle)]==needle

def extractStringWithinCharset(S,chrSet):
	newS=""
	for s in S:
		if s in chrSet:
			newS+=s
	
	return newS

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['out-seq','out-fasta'])
	
	mode="outseq"
	
	for o,v in opts:
		if o=='--out-seq':
			mode="outseq"
		elif o=='--out-fasta':
			mode="outfasta"
			
	
	refName=""
	
	try:
		infile,=args
	except:
		printUsageAndExit(programName)
	
	originStarted=False
		
	fil=open(infile)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		
		if hasPrefix(lin,"LOCUS"):
			locusSplit=lin.split()
			try:
				refName=locusSplit[1]

					
			except:
				pass
		
		elif hasPrefix(lin,"ORIGIN"):
			if mode=="outfasta":
				print >> stdout,">"+refName
			originStarted=True
		elif hasPrefix(lin,"//"):
			break
		elif originStarted:
			print >> stdout,extractStringWithinCharset(lin,"ACTGactgNnUu")
			
	
	fil.close()