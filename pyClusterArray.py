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
####
#
#  pyClusterArray.py version 1.1 <20100420>
#  Albert W. Cheng
#  awcheng@mit.edu
#  
#  Use Bio.cluster to cluster expression data on array and generate correlation matrix and dendrogram on array for JavaTreeView
#
#  Please redistribute or modify as needed, but remember to add your modification log here.
#  
#
#####



from Bio.Cluster.cluster import *
from Bio.Cluster import *
from numpy import std
from math import sqrt

import shutil
import sys
from sys import *

from getopt import getopt

def printUsage(programName):
	print >> stderr, "got command line"," ".join(argv)
	print >> stderr, programName,"[Options] filename dist method"
	print >> stderr, "This program takes in expression data and output array correlation (column-wise) dendrogram and correlation matrix for JavaTreeView"
	print >> stderr, "from PyCluster (see http://www.biopython.org/DIST/docs/api/Bio.Cluster.Record-class.html#treecluster)"
	print >> stderr, "dist     : specifies the distance function to be used:"
	print >> stderr, "           dist=='e': Euclidean distance"
	print >> stderr, "           dist=='b': City Block distance"
	print >> stderr, "           dist=='c': Pearson correlation"
	print >> stderr, "           dist=='a': absolute value of the correlation"
	print >> stderr, "           dist=='u': uncentered correlation"
	print >> stderr, "           dist=='x': absolute uncentered correlation"
	print >> stderr, "           dist=='s': Spearman's rank correlation"
	print >> stderr, "           dist=='k': Kendall's tau"
	print >> stderr, "method   : specifies which linkage method is used:"
	print >> stderr, "           method=='s': Single pairwise linkage"
	print >> stderr, "           method=='m': Complete (maximum) pairwise linkage (default)"
	print >> stderr, "           method=='c': Centroid linkage"
	print >> stderr, "           method=='a': Average pairwise linkage"
	print >> stderr, "Options:"
	print >> stderr,"--prefix outputprefix"
	print >> stderr, "-j jobname specify the jobname such that outputs are prefixed by jobname"
	print >> stderr, "-s seperator specify the separator used in the expression data file"
	print >> stderr, "-l base  log transform to log(base)" 
	print >> stderr, "-n NA left lower portion of matrix"
	print >> stderr, "-N NA right upper portion of matrix"
	print >> stderr, "--center-gene m=median,a=mean center gene prior to clustering"
	print >> stderr, "--normalize-gene normalize gene prior to clustering"
	print >> stderr, "--top-sd rank select only the top rank sd (all items >= top rank sd)"
	print >> stderr, "--ignore-NA-rows ignore rows with at least one NA value"
	print >> stderr, "Input Format:"
	print >> stderr, "First line: GeneID<tab>ArrayName1<tab>ArrayName2<tab>...ArrayNameN"
	print >> stderr, "Other lines: GeneID<tab>Data1<tab>Data2<tab>...DataN"			
	print >> stderr, "Outputs:"
	print >> stderr, "<jobname>.cdt The arrays correlation matrix for use in JavaTreeView"
	print >> stderr, "<jobname>_org.cdt The heatmap of original data for use in JavaTreeView"
	print >> stderr, "<jobname>.atr The array tree for use in JavaTreeView"
	print >> stderr, "<jobname>.mat.txt The correlation matrix table"

def makeCompleteMatrix(M):
	dimM=len(M)
	cM=[]	
	for r in range(0,dimM):
		curRow=[]
		cM.append(curRow)
		for c in range(0,dimM):
			if r==c:
				curRow.append(0)
			elif c>r:
				curRow.append(M[c][r])
			else:
				curRow.append(M[r][c])

	return cM

def complementDistanceMatrixInPlace(M):
	for row in M:
		for i in range(0,len(row)):
			row[i]=1.0-row[i]


def printMatrix(stream,M,prefixes):
	for row,prefix in zip(M,prefixes):
		for cell in row:
			print >> stream,"%.2f\t" % (cell),

		print >> stream,prefix


def findIndices(needles,haystack):
	indices=[]
	for needle in needles:
		indices.append(haystack.index(needle))

	return indices

def rearrangeColAndRowSqMatrix(M,from_indices):
	newM=[]
	lenM=len(M)
	for r in range(0,lenM):
		newRow=[]
		newM.append(newRow)
		for c in range(0,lenM):
			newRow.append(M[from_indices[r]][from_indices[c]])

	return newM

def removeExt(filename):
	filename=filename.split(".")
	if len(filename)>=2:
		del filename[len(filename)-1]
	
	return ".".join(filename)






def logTransformInPlace(L,Msk,logbase):
	if logbase<=0:
		return

	for i in range(0,len(L)):
		m=Msk[i]
		if m==0:
			continue
		try:
			L[i]=log(L[i])/logbase
		except:
			Msk[i]=0
	


def strArrayToFloatArrayInPlace(A,Msk):
	for i in range(0,len(A)):
		try:
			if A[i].lower() in ["nan","na","n\\a","n/a"]:
				raise ValueError
			A[i]=float(A[i])
			Msk.append(1)
		except:
			A[i]=0.0
			Msk.append(0)


def getNonMaskedRowValues(row,MskRow):
	nonmasked=[]
	for r,m in zip(row,MskRow):
		if m!=0:
			nonmasked.append(r)

	return nonmasked

def setRowValueWithMaskInPlace(row,MskRow,values):
	values_i=0
	row_i=0
	for row_i in range(0,len(MskRow)):
		if MskRow[row_i]!=0:
			row[row_i]=values[values_i]
			values_i+=1

	
	if values_i!=len(values):
		print >> stderr,"when setting row with masked in place values_i!=len(values at the end)"
		exit()

def sumOfSquares(L):
	sos=0.0
	for x in L:
		sos+=x*x;

	return sos

def cluster3_NormalizeInPlace(values):
	if len(values)<1:
		return

	sos=sumOfSquares(values)
	try:
		S=sqrt(1.0/sos)
	except ZeroDivisionError:
		return
	
	for k in range(0,len(values)):
		values[k]*=S
	

def cluster3_CenterInPlaceByMedian(values):
	Med=median(values)
	for k in range(0,len(values)):
		values[k]-=Med

def cluster3_CenterInPlaceByMean(values):
	Mean=mean(values)
	for k in range(0,len(values)):
		values[k]-=Mean
	
def normalizeGenePerRow(row,MskRow):
	nonmaskedRow=getNonMaskedRowValues(row,MskRow)
	cluster3_NormalizeInPlace(nonmaskedRow)
	setRowValueWithMaskInPlace(row,MskRow,nonmaskedRow)

	

def normalizeGenesInPlace(M,Msk):

	for Mrow,MskRow in zip(M,Msk):
		#print >> stderr,"b4",Mrow
		normalizeGenePerRow(Mrow,MskRow)
		#print >>  stderr,"aft",Mrow


def centerGeneByMedianPerRow(row,MskRow):
	nonmaskedRow=getNonMaskedRowValues(row,MskRow)
	cluster3_CenterInPlaceByMedian(nonmaskedRow) ####
	setRowValueWithMaskInPlace(row,MskRow,nonmaskedRow)	

def centerGeneByMeanPerRow(row,MskRow):
	nonmaskedRow=getNonMaskedRowValues(row,MskRow)
	cluster3_CenterInPlaceByMean(nonmaskedRow) ####
	setRowValueWithMaskInPlace(row,MskRow,nonmaskedRow)	

def centerGenesInPlaceByMedian(M,Msk):
	for Mrow,MskRow in zip(M,Msk):
		centerGeneByMedianPerRow(Mrow,MskRow)	

def centerGenesInPlaceByMean(M,Msk):
	for Mrow,MskRow in zip(M,Msk):
		centerGeneByMeanPerRow(Mrow,MskRow)		

def topSDSubM(M,Msk,k):
	SDs=[]

	if k>=len(M):
		return (M[:],Msk[:])
	
	for Mrow,MskRow in zip(M,Msk):
		nonmasked=getNonMaskedRowValues(Mrow,MskRow)
		sd=std(nonmasked)
		if str(sd)=="nan":
			print >> stderr,"nan sd=",nonmasked
		SDs.append(sd)

	
	SDs.sort(reverse=True)
	
	SDThreshold=SDs[k-1]

	print >> stderr,"SDThreshold=",SDThreshold
	
	newM=[]
	newMsk=[]
	for Mrow,MskRow,sd in zip(M,Msk,SDs):
		if sd>=SDThreshold:
			newM.append(Mrow)
			newMsk.append(MskRow)

	return (newM,newMsk)
	
def absArray(L):
	absL=[]
	for x in L:
		absL.append(fabs(x))
	
	return absL	


if __name__=="__main__":

	####MAIN ENTRY POINT
	programName=sys.argv[0]
	opts,args=getopt(sys.argv[1:],'s:j:nNl:',['center-gene=','normalize-gene','prefix','top-sd=','ignore-NA-rows','filled-threshold=','sd-threshold=','at-least-x-data-with-abs-val-ge-y=','max-min='])
	CenterGene=""
	NormalizeGene=False
	NALowerLeft=False
	NAUpperRight=False
	logbase=0
	prefix=""
	topSD=0
	#ignoreNARows=False
	SDThreshold=0.0
	filledThreshold=0.0
	atLeastXDataWithAbsValGEY=[0,0] #[X,Y]
	maxMin=0.0
	try:
		filename,distance,clustermethod=args

		separator="\t"
		jobname=removeExt(filename)

		for o,a in opts:
			if o=="-s":
				separator=a
			elif o=="-j":
				jobname=a
			elif o=='-n':
				NALowerLeft=True
			elif o=='-N':
				NAUpperRight=True
			elif o=='-l':
				logbase=log(float(a))
			elif o=="--center-gene":
				CenterGene=a
			elif o=="--normalize-gene":
				NormalizeGene=True
			elif o=="--prefix":
				prefix=a
			elif o=="--top-sd":
				topSD=int(a)
			elif o=='--ignore-NA-rows':
				#ignoreNARows=True
				filledThreshold=1
			elif o=='--filled-threshold':
				filledThreshold=float(v)
			elif o=='--sd-threshold':
				SDThreshold=float(v)
			elif o=='--at-least-x-data-with-abs-val-ge-y':
				try:
					x,y=v.split(",")
					atLeastXDataWithAbsValGEY=[int(x),float(y)]
				except:
					print >> stderr,"incorrect format for this option, got",v,".Use --at-least-x-data-with-abs-val-ge-y x:int,y:float"
					printUsageAndExit(programName)
			elif o=='--max-min':
				maxMin=float(v)

				
	except:
		printUsage(programName)
		sys.exit()


	M=[]
	MASK=[]
	Genes=[]
	Arrays=[]
	UNIQID=""

	lino=0

	print >> stderr,"reading record from",filename

	fil=open(filename)

	for lin in fil:
		lino+=1
		if lino%100000==1:
			print >> sys.stderr,"reading in line",lino

		lin=lin.rstrip()
		fields=lin.split(separator)
		if lino==1:
			Arrays=fields[1:]
			UNIQID=fields[0]
		else:	
			Genes.append(fields[0])
			tM=fields[1:]
			Msk=[]
			strArrayToFloatArrayInPlace(tM,Msk)

			

			if filledThreshold>0.0:			
				filled=float(Msk.count(1))
				if filled/len(Msk)<filledThreshold:
					continue #not enough filled values in the row

			nonmasked=getNonMaskedRowValues(tM,Msk)

			Xc,Yc=atLeastXDataWithAbsValGEY

			if Xc>0:
				Xn=0
				for x in nonmasked:
					if fabs(x)>=Yc:
						Xn+=1

				if Xn<Xc:
					continue #At least X data with abs val >= Y not passed


			if maxMin>0.0:
				if max(nonmasked)-min(nonmasked)<maxMin:
					continue #Max-Min not passed
			
			if SDThreshold>0.0:
				sd=std(nonmasked)
				if sd<SDThreshold:
					continue #SD Threshold not passed

			
			
				
			
			logTransformInPlace(tM,Msk,logbase)
			M.append(tM)
			MASK.append(Msk)



	fil.close()	
	print >> stderr,"done reading"

	if topSD>0:
		M,MASK=topSDSubM(M,MASK,topSD)	

	

	if CenterGene=="m":
		print >> stderr,"center gene by median"
		centerGenesInPlaceByMedian(M,MASK)
	elif CenterGene=="a":
		print >> stderr,"center gene by mean"
		centerGenesInPlaceByMean(M,MASK)
	elif CenterGene!="":
		print >> stderr,"unknown way to center gene",centerGene
		exit()

	
	if NormalizeGene:
		print >> stderr,"normalize gene"
		normalizeGenesInPlace(M,MASK)

	
	


	#now fill in gene record
	#seems faster than the Record(file_handle) provided by PyCluster
	record=Record()
	record.data=M
	record.mask=MASK
	record.geneid=Genes
	record.genename=Genes
	record.expid=Arrays
	record.uniqid=UNIQID

	#record= Record(fil)

	#fil.close()

	#print >> stderr,record
	print >> stderr,"generate tree and correlation matrix"
	ArrayTree=record.treecluster(transpose=1,method=clustermethod,dist=distance)
	Darray=record.distancematrix(transpose=1,dist=distance)
	ComArrayMatrix=makeCompleteMatrix(Darray)
	complementDistanceMatrixInPlace(ComArrayMatrix)
	print >> stderr,"saving files"
	record.save(jobname,expclusters=ArrayTree)






	#now read in jobname.cdt and modify it (needs only first three lines)

	fil=open(jobname+".cdt")
	firstthreelines=[]
	lino=0
	for lin in fil:
		lino+=1
		if lino>3:
			break
		lin=lin.rstrip()
		firstthreelines.append(lin)
		if lino==1:
			fields=lin.split("\t")	
			arrayOrdered=fields[3:]


	fil.close()

	#move the original cdt to a new name
	shutil.move(jobname+".cdt",jobname+"_orig.cdt")
	#now rewrite

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=rearrangeColAndRowSqMatrix(ComArrayMatrix,findIndices(arrayOrdered,Arrays))

	for i in range(0,len(arrayOrdered)): #row
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)): #col
			if NALowerLeft and i>j:
				print >> fil, "\t"+"NA",
			elif NAUpperRight and j>i:
				print >> fil, "\t"+"NA",
			else:
				print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()


	print >> stderr,"Outputting Matrix"
	fil=open(jobname+".mat.txt","w")

	print >> fil, "Correlation Matrix (Not Clustered)"
	print >> fil,"\t".join(Arrays)
	printMatrix(fil, ComArrayMatrix, Arrays)

	print >> fil, "Correlation Matrix (Clustered)"
	print >> fil,"\t".join(arrayOrdered)
	printMatrix(fil, rearrangedCorrMatrix, arrayOrdered)
	fil.close()
	print >> stderr,"< DONE"," ".join(sys.argv),">"


		
