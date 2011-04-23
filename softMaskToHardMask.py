#!/usr/bin/python

from sys import *

def generic_istream(filename):
	#print >> stderr,"opening ",filename
	if filename=="-":
		return sys.stdin
	else:
		return open(filename)


def printUsageAndExit(programName):
	print >> stderr,programName,"fastafile > outfile"
	exit()


def softMaskToHardMaskSeq(seq):
	nseq=""
	for s in seq:
		if s.islower():
			nseq+="N"
		else:
			nseq+=s
	return nseq
	
if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
		
	
	fil=generic_istream(filename)
	for lin in fil:
		lin=lin.strip()
		if len(lin)<1:
			continue
		if lin[0]!=">": #header ignore
			lin=softMaskToHardMaskSeq(lin) #convert soft to hard
		
		print >> stdout,lin
	
	fil.close()
