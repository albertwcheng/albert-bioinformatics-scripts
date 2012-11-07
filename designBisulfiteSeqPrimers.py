#!/usr/bin/env python
from sys import *
from getopt import getopt


def simpleTmFromACGTNum(numA,numC,numG,numT,N):
	if N<14:
		return (numA+numT)*2+(numG+numC)*4
	
	return 64.9+41*(numG+numC-16.4)/N	
	

def simpleTmOfSeq(seq):
	numA=0
	numC=0
	numG=0
	numT=0
	for s in seq:
		if s in 'Aa':
			numA+=1
		elif s in 'Cc':
			numC+=1
		elif s in 'Gg':
			numG+=1
		elif s in 'TtUu':
			numT+=1	
		else:
			print >> stderr,"unknown character %s" %(s)
			raise TypeError
			
	N=len(seq)
	return simpleTmFromACGTNum(numA,numC,numG,numT,N)
	

def listAllPrimersAvoidtG(seq,minL,maxL,minTm,maxTm,reportAtMost):
	for i in range(0,len(seq)-minL+1):
		reported=0
		for j in range(i+minL,i+maxL):
		
			thisTm=simpleTmOfSeq(seq[i:j])
			
			if "tG" in seq[i:j]:
				break
			
			if thisTm>=minTm and thisTm<=maxTm:
				reported+=1
				print >> stdout,"%d\t%d\t%d\t%f\t%s" %(i+1,j,j-i,thisTm,seq[i:j])
			if reported==reportAtMost:
				break
			if thisTm>maxTm:
				break

if __name__=='__main__':
	#seq="CTaCACCCCCACCCCTAaCT"
	#print >> stdout,"%s Tm=%f" %(seq,simpleTmOfSeq(seq))
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['minL=','maxL=','minTm=','maxTm=','reportAtMost='])
	
	minL=20
	maxL=30
	minTm=55
	maxTm=65
	reportAtMost=1
	
	for o,v in opts:
		if o=='--minL':
			minL=int(v)
		elif o=='--maxL':
			maxL=int(v)
		elif o=='--minTm':
			minTm=float(v)
		elif o=='--maxTm':
			maxTm=float(v)
		elif o=='--reportAtMost':
			reportAtMost=int(v)
	try:
		filename,=args
	except:
		print >> stderr,programName,"[options] filename"
		print >> stderr,"Options:"
		print >> stderr,"--minL minlength [default: 20]"
		print >> stderr,"--maxL maxlength [default: 30]"
		print >> stderr,"--minTm min Tm [default: 55]"
		print >> stderr,"--maxTm max Tm [default: 65]"
		print >> stderr,"--reportAtMost report at most numPrimers for each starting position [default: 1]"
		exit(1)
		
	minL=int(minL)
	maxL=int(maxL)
	minTm=float(minTm)
	maxTm=float(maxTm)
	
	
	fil=open(filename)
	seq=""
	for lin in fil:
		lin=lin.strip()
		if len(lin)<1:
			continue
		if lin[0]=='>':
			continue
		seq+=lin
	
	listAllPrimersAvoidtG(seq,minL,maxL,minTm,maxTm,reportAtMost)
	
		
		
		
	