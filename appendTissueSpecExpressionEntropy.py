#!/usr/bin/env python

from math import log
from sys import *
from albertcommon import *

def entropy(values):
	#transform values such that all values above 0
	mvalues=min(values)
	if mvalues<0:
		for i in range(0,len(values)):
			values[i]-=mvalues
	
	totalwgt=float(sum(values))
	
	if totalwgt==0:
		return "NA"
	
	Hg=0.0
	for wgt in values:
		try:
			Ptg=wgt/totalwgt
			if Ptg<0:
				print >> stderr,"Ptg<0, should not happen. abort"
				exit(1)
			if Ptg==0:
				continue #Ptg==0, don't contribute to entropy?
			#print >> stderr,Ptg
			Hg-=1*Ptg*log(Ptg,2)
		except:
			print >> stderr,"values=",values,"Ptg=%f wgt=%f totalwgt=%f Hg=%f" %(Ptg,wgt,totalwgt,Hg)
			exit(1)
			pass
			
	return Hg

def toFloatList(fields,noise):
	values=[]
	for f in fields:
		try:
			values.append(float(f)+noise)
		except:
			pass
			
	return values
		
noise=0.000000  


if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		matrix,valcols=args
	except:
		print >> stderr,programName,"matrixFile valcols > outputFileWithHgAppended"
		explainColumns(stderr)
		exit()
	
	fs="\t"
	startRow=2
	headerRow=1
		
	header,prestarts=getHeader(matrix,headerRow,startRow,fs)
		
	valcols=getCol0ListFromCol1ListStringAdv(header,valcols)
	
	lino=0
	fil=open(matrix)
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		if lino<startRow:
			fields+=["Hg"]
		else:
			values=toFloatList(getSubvector(fields,valcols),noise)
			if len(values)==0:
				Hg="NA"
			else:
				try:
					Hg=entropy(values)
				except:
					Hg="NA"
					
			fields+=[str(Hg)]
		print >> stdout,fs.join(fields)
		
	fil.close()