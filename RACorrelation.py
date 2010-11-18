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
#uses Liao and Zhang, 2006 RA approach

from albertcommon import *
from sys import *
from getopt import getopt
from math import *
from Bio.Cluster.cluster import *
from Bio.Cluster import *
from numpy import std,mean,median,arcsinh
from quantileNormalize import quantileNormalizeMInPlace

#def median(x):
#	x2=x[:]
#	x2.sort()
#	L=len(x2)
#	if L%2==0:
#		return (float(x2[L/2-1])+x2[L/2])/2
#	else:
#		return x2[L/2]


#species groupings [ [col,..] , ...] G
#data matrix [ [ S(i,j) ... ] ]  M





def transformToRAValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			sumS=sum(subv)
			for j in group:
				Mp[i][j]=float(row[j])/sumS
	return Mp

def transformToRAasinhValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			sumS=sum(subv)
			for j in group:
				Mp[i][j]=arcsinh(float(row[j])/sumS)
	return Mp

def transformToRAMSasinhValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			sumS=sum(subv)
			medianS=median(subv)
			for j in group:
				Mp[i][j]=arcsinh(float(row[j])-medianS/sumS)
	return Mp




def transformToRAMSValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			medianS=median(subv)
			sumS=sum(subv)
			for j in group:
				Mp[i][j]=(float(row[j])-medianS)/sumS
	return Mp


def transformToRAstdValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			meanS=mean(subv)
			stdS=std(subv)
			for j in group:
				Mp[i][j]=(float(row[j])-meanS)/stdS
	return Mp

def transformToRA2stdValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			medianS=median(subv)
			stdS=std(subv)
			for j in group:
				Mp[i][j]=(float(row[j])-medianS)/stdS
	return Mp


def sumOfSquares(L):
	sos=0.0
	for x in L:
		sos+=x*x;

	return sos

def transformToRA3stdValues(M,G,startRow):
	Mp=M[:] #just make a copy first, then replace their values
	for i in range(startRow,len(M)):
		row=M[i]
		for group in G:
			subv=getSubvector(row,group)
			medianS=median(subv)
			#stdS=std(subv)
			for k in range(0,len(subv)):
				subv[k]=subv[k]-medianS
			
			sos=sumOfSquares(subv)
			S=sqrt(1/sos)
			for k in range(0,len(subv)):
				subv[k]=subv[k]*S

			for j,newValue in zip(group,subv):
				Mp[i][j]=newValue #median subtraction

			#now normalize
			
			
			
	return Mp





def RACorrel_inner(Mp,j1,j2,startRow):
	N=len(Mp)
	sumJ1J2=0
	sumJ1=0
	sumJ2=0
	sumJ1sq=0
	sumJ2sq=0

	for i in range(startRow,N):
		sumJ1J2+=Mp[i][j1]*Mp[i][j2]
		sumJ1+=Mp[i][j1]
		sumJ2+=Mp[i][j2]
		sumJ1sq+=Mp[i][j1]*Mp[i][j1]
		sumJ2sq+=Mp[i][j2]*Mp[i][j2]

	r=(sumJ1J2-sumJ1*sumJ2/N)/(sqrt(sumJ1sq-(sumJ1*sumJ1)/N)*sqrt(sumJ2sq-(sumJ2*sumJ2)/N))
	return r

def distMatrix(C):
	#print >> stderr,C
	D=[]
	for row in C:
		Drow=[]
		D.append(Drow)
		for r in row:
			#print >> stderr, r
			Drow.append(1.0-r)

	return D

def RACorrelation(Mp,colExt):
	
	C=[]
	for j1 in colExt:
		Crow=[]
		C.append(Crow)		
		for j2 in colExt:
			if j1==j2:
				Crow.append(1)
			elif j1>j2:
				Crow.append('na')
			else:
				#the real calculation is here
				Crow.append(RACorrel_inner(Mp,j1,j2,startRow))

	for j1 in range(0,len(C)):
		for j2 in range(0,len(C)):
			if j1>j2:
				if C[j1][j2]=='na':
					C[j1][j2]=C[j2][j1]
				else:
					C[j2][j1]=C[j1][j2]
		
	return C

def convertToFloatInPlace(M,groups,startRow):
	for i in range(startRow,len(M)):
		for group in groups:
			for j in group:
				#print >> stderr, i,j
				M[i][j]=float(M[i][j])


def writeMatrix(stream,M,fs):
	
	for row0 in M:
		row=row0[:]
		for j in range(0,len(row)):
			row[j]=str(row[j])
		print >> stream, fs.join(row)					


def logtransform(M,logj,logb,startRow):
	if len(logj)==0:
		return
	b=log(logb)
	for i in range(startRow,len(M)):
		for j in logj:
			M[i][j]=log(M[i][j])/b

def normalizeSumOfSquare(M,groups,startRow):
	for i in range(startRow,len(M)):
		row=M[i]
		for group in groups:
			subv=getSubvector(row,group)
			sos=sumOfSquares(subv)
			S=sqrt(1/sos)
			for j in group:
				M[i][j]=M[i][j]*S

def quantileNorm(M,groups,startRow,method):
	Mp=[]
	lM=len(M)
	for i in range(startRow,lM):
		row=M[i]
		print >> stderr,"normalizing",(i+1),"of",lM		
		for group in groups:
			subv=getSubvector(row,group)
			Mp.append(subv)
			quantileNormalizeMInPlace(Mp,method)
		
		for Mpsubv,group in zip(Mp,groups):
			for j,newValue in zip(group,Mpsubv):
				M[i][j]=newValue






def printUsageAndExit(programName):
	print >> stderr, programName,"-g cols -g cols [ -l cols : log transform cols ] [--norm-sos --quantile-norm method='min,max,mean,sum,rank'] ... [ -r output-ra-file-name -m *RA|RAMS|std|std2|std3:using median subtraction ] filename > correlmatrix"
	explainColumns(stderr)
	exit()

if __name__=='__main__':
	programName=argv[0]
	startRow=2
	headerRow=1
	fs="\t"
	rafilename=""
	mode="RA"
	normSOS=False
	quantileNormalize=""

	colExt=[]
	colLogT=[]
	logb=2

	opts,args=getopt(argv[1:],'g:r:m:l:',['norm-sos','quantile-norm='])
	try:
		filename,=args
	except:
		printUsageAndExit(programName)


	header,prestarts=getHeader(filename,headerRow,startRow,fs)

	
	
	

	
	groupings=[]
	for o,v in opts:
		if o=='-g':
			cols=getCol0ListFromCol1ListStringAdv(header,v)
			groupings.append(cols)
			colExt.extend(cols)
		elif o=='-l':
			cols=getCol0ListFromCol1ListStringAdv(header,v)
			colLogT.extend(cols)			
		elif o=='-r':
			rafilename=v
		elif o=='-m':
			mode=v
		elif o=='--norm-sos':
			normSOS=True
		elif o=='--quantile-norm':
			quantileNormalize=v

	#now read in file
	#read into M
	M=[]
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip()		
		row=lin.split(fs)
		if len(row)<2:
			continue
		M.append(row)
		

	fil.close()

	#now convert relevant col to float
	convertToFloatInPlace(M,groupings,startRow-1)

	logtransform(M,colLogT,logb,startRow-1)
	
	if mode=="RA":
		Mp=transformToRAValues(M,groupings,startRow-1)
	elif mode=="RAasinh":
		Mp=transformToRAasinhValues(M,groupings,startRow-1)
	elif mode=="RAMS":
		Mp=transformToRAMSValues(M,groupings,startRow-1)
	elif mode=="RAMSasinh":
		Mp=transformToRAMSasinhValues(M,groupings,startRow-1)
	elif mode=="std":
		Mp=transformToRAstdValues(M,groupings,startRow-1)
	elif mode=="std2":
		Mp=transformToRA2stdValues(M,groupings,startRow-1)
	elif mode=="std3":
		Mp=transformToRA3stdValues(M,groupings,startRow-1)
	else:
		print >> stderr,"unknown mode",mode
		printUsageAndExit(programName)
	
	if normSOS:
		print >> stderr,"normalize sum of squares"
		normalizeSumOfSquare(M,groupings,startRow-1)
	
	if quantileNormalize!="":
		print >> stderr,"quantile normalize by",quantileNormalize
		quantileNorm(M,groupings,startRow-1,quantileNormalize)


	if rafilename!="":
		print >> stderr,"outputing RA file to",rafilename
		fout=open(rafilename,"w")
		writeMatrix(fout,Mp,fs)
		fout.close()

	#now do correlation:
	C=RACorrelation(Mp,colExt)
	
	nameExt=getSubvector(header,colExt)
	#print >> stderr, C
	D=distMatrix(C)
	tree=treecluster(distancematrix=D) #no need to transpose

	record=Record()
	#print >> stderr,C
	record.data=C
	record.geneid=nameExt
	record.genename=nameExt
	record.expid=nameExt
	record.uniqid="RA"
	record.save(filename,expclusters=tree,geneclusters=tree)


	#now output correlation
	for r in range(0,len(C)):
		C[r].insert(0,nameExt[r])
		
	C.insert(0,["Pearson"]+nameExt)
	writeMatrix(stdout,C,fs)

	
	#record._savetree(filename,tree,arange,1)

	print >> stderr,"<Done>"

		
	
	
