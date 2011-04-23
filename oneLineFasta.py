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

	
if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
		
	firstLine=True
	
	seqlin=""
	
	fil=generic_istream(filename)
	for lin in fil:
		lin=lin.strip()
		if lin[0]==">": #header ignore
			
			
			if firstLine:	
				firstLine=False
			else:
				print >> stdout,seqlin
			print >> stdout,lin
			seqlin=""
		else:
			#print >> stdout,lin,
			seqlin+=lin
			
	print >> stdout,seqlin
		
	fil.close()
