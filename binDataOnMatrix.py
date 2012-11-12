#!/usr/bin/env python

from sys import *
from albertcommon import *
from getopt import getopt
from numpy import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] filename"
	print >> stderr,"Options:"
	print >> stderr,"--min set the min of the bins [default: detect the min in data]"
	print >> stderr,"--max set the max of the bins [default: detect the max in data]"
	print >> stderr,"--nbins set the number of bins [default: 11]"
	print >> stderr,"--bins [x1,x2,x3...,xN], or range(x,y) or linspace(s,e,nbins) some other python code. directly set the bin lower bounds"
	print >> stderr,"--cols colRange. operate on these range only [default: 2-_1]"
	print >> stderr,"--ceiling f. set the ceiling above the max by 1+f [default: f=0.1]" 
	print >> stderr,"--keycol col [default: 1]"
	explainColumns(stderr)
	exit(1)
	
def StrListToFloatListIgnoreErrors(S):
	L=[]
	for s in S:
		try:
			L.append(float(s))
		except:
			pass
	return L

def getProbVector(V):
	sumV=sum(V)
	p=[]
	for v in V:
		p.append(float(v)/sumV)
	return p
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['min=','max=','nbins=','bins=','cols=','ceiling=','keycol='])
	
	
	minBins=None
	maxBins=None
	nbins=11
	cols="2-_1"
	ceiling=0.1
	bins=None
	headerRow=1
	startRow=2
	fs="\t"
	keycol="1"
	
	for o,v in opts:
		if o=='--min':
			minBins=float(v)
		elif o=='--max':
			maxBins=float(v)
		elif o=='--nbins':
			nbins=int(v)
		elif o=='--bins':
			bins=eval(v)
		elif o=='--cols':
			cols=v
		elif o=='--ceiling':
			ceiling=float(v)
		elif o=='--keycol':
			keycol=v
	
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
	
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	cols=getCol0ListFromCol1ListStringAdv(header,cols)
	keycol=getCol0ListFromCol1ListStringAdv(header,keycol)[0]
	
	
	#if bins not defined and ( minBins or maxBins not defined). first pass:
	if bins==None and ( minBins==None or maxBins==None ):
		minValue=None
		maxValue=None
		
		fil=open(filename)
		
		lino=0
		for lin in fil:
			lino+=1
			if lino<startRow:
				continue
			lin=lin.rstrip("\r\n")
			fields=lin.split(fs)
			values=StrListToFloatListIgnoreErrors(getSubvector(fields,cols))
			if minValue==None:
				try:
					minValue=min(values)
				except:
					pass
			else:
				minValue=min(minValue,min(values))
				
			if maxValue==None:
				try:
					maxValue=max(values)
				except:
					pass
			else:
				maxValue=max(maxValue,max(values))				
		
		fil.close()	
		
		if minBins==None:
			minBins=minValue
		
		if maxBins==None:
			maxBins=maxValue*(1+ceiling)
		
	if bins==None:
		bins=linspace(minBins,maxBins,nbins)
	
	print >> stdout,fs.join(["key"]+toStrList(bins))
	
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		values=StrListToFloatListIgnoreErrors(getSubvector(fields,cols))
		#print >> stderr,"values:",values
		if len(values)==0:
			print >> stdout,fs.join([fields[keycol]]+(['NA']*len(bins)))
		else:
			bincounts=[0]*len(bins)
			digitized=digitize(values,bins)
			#print >> stderr,"degit",digitized
			for digix in digitized:
				bincounts[digix-1]+=1
			
			binp=getProbVector(bincounts)
			print >> stdout,fs.join([fields[keycol]]+toStrList(binp))
			
			
						
	fil.close()
			
		