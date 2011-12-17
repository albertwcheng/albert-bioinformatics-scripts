#!/usr/bin/env python

from math import log
from sys import *
from albertcommon import *

def entropy(values):
	totalwgt=float(sum(values))
	Hg=0.0
	for wgt in values:
		try:
			Ptg=wgt/totalwgt
			#print >> stderr,Ptg
			Hg-=1*Ptg*log(Ptg,2)
		except:
			print >> stderr,values
			print >> stderr,"Ptg=%f wgt=%f totalwgt=%f Hg=%f" %(Ptg,wgt,totalwgt,Hg)
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
		
noise=0.000001


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