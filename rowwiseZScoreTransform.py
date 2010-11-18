#!/usr/bin/python

'''



Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

from numpy import mean,median,std
from math import sqrt
from sys import *
from albertcommon import *
from getopt import getopt
from transformToPercentile import transformValueMatrixToRankMatrix
#rowwiseZScoreTransform.py

#def sampleSD(L):
#	return std(L,ddof=1)

def transposeMatrix(M):
	Mp=[]	
	ncols=len(M[0])
	nrows=len(M)
	for c in range(0,ncols):
		MpRow=[]
		Mp.append(MpRow)
		for r in range(0,nrows):
			MpRow.append(M[r][c])
	return Mp
	
def toStrArray(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL
	
def toFloatArray(L):
	fL=[]
	for s in L:
		fL.append(float(s))
	return fL

def standardizeInPlaceMedian(L,std_ddof):
	MEDIAN=median(L)
	STD=std(L,ddof=std_ddof)
	for i in range(0,len(L)):
		L[i]=(L[i]-MEDIAN)/STD

def standardizeInPlaceMean(L,std_ddof):
	MEAN=mean(L)
	STD=std(L,ddof=std_ddof)
	for i in range(0,len(L)):
		L[i]=(L[i]-MEAN)/STD		

def mulInPlace(L,x):
	for i in range(0,len(L)):
		L[i]*=x
	

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['use-median','std-ddof=','mul','row-wise-percentile'])
	try:
		filename,valCols=args
	except:
		print >> stderr,programName,"[options] filename valCols"
		print >> stderr,"options"
		print >> stderr,"--use-median  use median instead of mean in z-score calculation"
		print >> stderr,"--std-ddof ddf set delta degree of freedom (std uses N-ddof as denominator) [default: 1]"
		print >> stderr,"--mul x multiple z-score by x"
		print >> stderr,"--row-wise-percentile output row-wise percentile instead of z-score"
		explainColumns(stderr)
		exit()

	rowwisepercentile=False
	stdddof=1
	useMean=True
	headerRow=1
	startRow=headerRow+1
	fs="\t"
	mul=1.0

	for o,v in opts:
		if o=='--use-median':
			useMean=False
		elif o=='--std-ddof':
			stdddof=int(v)
		elif o=='--mul':
			mul=float(v)
		elif o=='--row-wise-percentile':
			rowwisepercentile=True

	header,prestarts=getHeader(filename,headerRow,startRow,fs)	
	valCols=getCol0ListFromCol1ListStringAdv(header,valCols)
	
	fil=open(filename)
	
	lino=0
	
	for lin in fil:
		lino+=1
		fields=lin.strip().split(fs)
		
		if lino>=startRow:
			#need transform
			try:			
				vals=toFloatArray(getSubvector(fields,valCols))
			except IndexError:
				print >> stderr,"@",lino				
				print >> stderr,fields
				print >> stderr,len(fields)
				print >> stderr,valCols
				print >> stderr,len(valCols)
								
				exit()	
			#print >> stderr,vals,"std=",sampleSD(vals),
			#print >> stderr,"median=",median(vals)

			if rowwisepercentile:
				Mp=transposeMatrix([vals])
				transformValueMatrixToRankMatrix(Mp)
				vals=transposeMatrix(Mp)[0]		
			else:
				if useMean:
					standardizeInPlaceMean(vals,stdddof)  
				else: #useMedian
					standardizeInPlaceMedian(vals,stdddof)  
						
			

			if mul!=1.0:
				mulInPlace(vals,mul)

			for val,colI in zip(vals,valCols):
				fields[colI]=str(val)
		
		print >> stdout,fs.join(fields)
		
	fil.close()
	
	
	
	
	
