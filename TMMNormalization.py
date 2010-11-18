#!/usr/bin/env python

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

from math import *
from sys import *
from albertcommon import *

def mean(L):
	return float(sum(L))/len(L)

def log2(x):
	return log(x,2)

def TMMnormalizationFactor(obs,ref,logratioTrim=0.3,sumTrim=0.05,doWeighting=True,Acutoff=-1e10):
	if obs==ref:
		return 1

	nO=sum(obs)
	nR=sum(ref)
	
	logR=[]
	absE=[]
	v=[]
	for o,r in zip(obs,ref):
		if o==0 or r==0:
			continue

		if o=="nan" or r=="nan":
			continue

		oden=float(o)/nO
		rden=float(r)/nR
		
		try:
			lo=log2(oden)
			lr=log2(rden)
		except:
			continue

		thisAbsE=(lo+lr)/2
		thisLogR=(lo-lr)

		if thisAbsE<=Acutoff:
			continue

		logR.append(thisLogR)
		absE.append(thisAbsE)

		v.append(float(nO-o)/nO/o + float(nR-r)/nR/r)

		
		
	
	#finished adding valid logR (M) and absE (A) and v (wrgk)
	
	#now trim values
	logRUpper=percentileOfList(1-logratioTrim,logR)
	logRLower=percentileOfList(logratioTrim,logR)
	absEUpper=percentileOfList(1-sumTrim,absE)
	absELower=percentileOfList(sumTrim,absE)

	newLogR=[]
	newAbsE=[]
	newV=[]	
	if doWeighting:
		Top=[]
		Bottom=[]

	for thisLogR,thisAbsE,thisV in zip(logR,absE,v):
		if thisLogR>=logRUpper or thisLogR<=logRLower:
			continue
		if thisAbsE>=absEUpper or thisAbsE<=absELower:
			continue

		

		newLogR.append(thisLogR)
		newAbsE.append(thisAbsE)
		newV.append(thisV)
		
		if doWeighting:
			Top.append(float(thisLogR)/thisV)
			Bottom.append(float(1)/thisV)

	#now replace
	logR=newLogR
	absE=newAbsE
	v=newV

	#now compute the normalization factor

	if doWeighting:
		logTMM=sum(Top)/sum(Bottom)
		return pow(2,logTMM)
	else:
		return pow(2,fpomean(logR))
		
	
def printUsageAndExit(programName):
	print >> stderr,programName,"matrixFile"
	exit()
		
if __name__=="__main__":
	programName=argv[0]
	try:
		filename,=argv[1:]
	except:
		printUsageAndExit(programName)

	obs=[]
	ref=[]
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip()
		fields=lin.split("\t")
		
		ref.append(float(fields[1]))
		obs.append(float(fields[2]))

	fil.close()

	factor=TMMnormalizationFactor(obs,ref)

	print >> stderr,"TMM factor:",factor


