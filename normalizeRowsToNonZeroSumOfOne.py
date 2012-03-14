#!/usr/bin/env python

from sys import *


def printUsageAndExit(programName):
	print >> stderr,programName,"infile > outfile"
	print >> stderr,"This program first transform values of each row such that the smallest value is 0, then it normalize the sum of the row to 1. Remove all rows with all zeros"
	print >> stderr,"This is for proper downstream use as probability vector per row"
	exit(1)

def toFloatList(L):
	fL=[]
	for x in L:
		fL.append(float(x))
	return fL

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
	lino=0
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		if lino==1:
			print >> stdout,lin
		else:
			fields=lin.split("\t")
			values=toFloatList(fields[1:])
			mvalues=min(values)
			if mvalues<0:
				for i in range(0,len(values)):
					values-=mvalues
			svalues=sum(values)
			if svalues==0.0:
				continue
			fields=[fields[0]]
			for value in values:
				fields.append(str(value/svalues))
				
			print >> stdout,"\t".join(fields)
	
	
	fil.close()