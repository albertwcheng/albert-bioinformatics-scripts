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

import numpy
from math import sqrt,log,fabs
#from cluster_init import *
from os.path import dirname,exists
from os import mkdir
from scipy.stats.stats import *
from matrixTranspose import *
from numpy import std

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
	print >> stderr, "-f,--folder specify the folder to put outputs"
	print >> stderr, "-p,--attach-param attach run parameters to output filenames"
	print >> stderr, "-s seperator specify the separator used in the expression data file"
	print >> stderr, "-l base  log transform to log(base)" 
	print >> stderr, "-n NA left lower portion of matrix"
	print >> stderr, "-N NA right upper portion of matrix"
	print >> stderr, "--center-gene m=median,a=mean center gene prior to clustering"
	print >> stderr, "--normalize-gene normalize gene prior to clustering"
 	print >> stderr, "--sd-threshold filter items >= sdt"	
	print >> stderr, "--top-sd rank select only the top rank sd (all items >= top rank sd)"
	print >> stderr, "--top-cv rank select only the top rank CV [=sd/absmean] (all items >= top rank cv)"
	print >> stderr, "--ignore-NA-rows ignore rows with at least one NA value"
	print >> stderr, "--ignore-NA-rows ignore rows with at least one NA value"
	print >> stderr, "--copy-array-tree-for-orig  copy the atr to _orig.atr as well"
	print >> stderr, "--out-pvalue-matrix  output also p-value matrix (for pearson and spearman correlation)"
	print >> stderr, "--out-processed-data output processed data and mask matrices to <jobname>.processed_data and <jobname>.processed_mask respectively"
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


def toStrList(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL



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
	if sos==0: #ignore all-0 row, can't normalize anyway
		return
	try:
		S=sqrt(1.0/sos)
	except ZeroDivisionError:
		return
	
	for k in range(0,len(values)):
		values[k]*=S
	

def cluster3_CenterInPlaceByMedian(values):
	Med=numpy.median(values)
	for k in range(0,len(values)):
		values[k]-=Med

def cluster3_CenterInPlaceByMean(values):
	Mean=numpy.mean(values)
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

def topSDSubM(Genes,M,Msk,k):
	SDs=[]

	if k>=len(M):
		return (M[:],Msk[:])
	
	for Mrow,MskRow in zip(M,Msk):
		nonmasked=getNonMaskedRowValues(Mrow,MskRow)
		sd=numpy.std(nonmasked)
		if str(sd)=="nan":
			print >> stderr,"nan sd=",nonmasked
		SDs.append(sd)

	
	SDSort=SDs[:]
	SDSort.sort(reverse=True)
	
	SDThreshold=SDSort[k-1]

	print >> stderr,"SDThreshold=",SDThreshold
	
	newM=[]
	newMsk=[]
	newGenes=[]
	for gene,Mrow,MskRow,sd in zip(Genes,M,Msk,SDs):
		if sd>=SDThreshold:
			newM.append(Mrow)
			newMsk.append(MskRow)
			newGenes.append(gene)
			
	return (newGenes,newM,newMsk)
	
	
def topCVSubM(Genes,M,Msk,k):
	SDs=[]

	if k>=len(M):
		return (M[:],Msk[:])
	
	for Mrow,MskRow in zip(M,Msk):
		nonmasked=getNonMaskedRowValues(Mrow,MskRow)
		sd=numpy.std(nonmasked)
		absmean=fabs(numpy.mean(nonmasked))
		CV=sd/absmean
		if str(sd)=="nan":
			print >> stderr,"nan sd=",nonmasked
		SDs.append(CV)

	
	SDSort=SDs[:]
	SDSort.sort(reverse=True)
	
	SDThreshold=SDSort[k-1]


	print >> stderr,"CVThreshold=",SDThreshold
	
	newM=[]
	newMsk=[]
	newGenes=[]
	for gene,Mrow,MskRow,sd in zip(Genes,M,Msk,SDs):
		if sd>=SDThreshold:
			newM.append(Mrow)
			newMsk.append(MskRow)
			newGenes.append(gene)
			
	return (newGenes,newM,newMsk)
	
def absArray(L):
	absL=[]
	for x in L:
		absL.append(fabs(x))
	
	return absL	

def getNonMaskedRowValuePairs(tM1,tMask1,tM2,tMask2):
	tM1nm=[]
	tM2nm=[]
	for tM1v,tMask1v,tM2v,tMask2v in zip(tM1,tMask1,tM2,tMask2):
		if tMask1v!=0 and tMask2v!=0:
			tM1nm.append(tM1v)
			tM2nm.append(tM2v)
	return (tM1nm,tM2nm)

def getSign(x):
	if x>=0:
		return 1
	else:
		return -1

if __name__=="__main__":

	####MAIN ENTRY POINT
	programName=sys.argv[0]
	opts,args=getopt(sys.argv[1:],'s:j:nNl:pf:',['center-gene=','normalize-gene','prefix','top-sd=','top-cv=','ignore-NA-rows','filled-threshold=','sd-threshold=','at-least-x-data-with-abs-val-ge-y=','max-min=','attach-param','folder=',"copy-array-tree-for-orig","out-pvalue-matrix","out-processed-data"])
	CenterGene=""
	NormalizeGene=False
	NALowerLeft=False
	NAUpperRight=False
	logbase=0
	prefix=""
	topSD=0
	topCV=0
	#ignoreNARows=False
	SDThreshold=0.0
	CVThreshold=0.0
	filledThreshold=0.0
	atLeastXDataWithAbsValGEY=[0,0] #[X,Y]
	maxMin=0.0
	attachParam=False
	folder=""
	copyArrayTreeForOrig=False
	pvalueMatrix=False
	logbaseDisplay=""
	outProcessedData=False
	
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
				logbaseDisplay=a
				logbase=log(float(a))
			elif o=="--center-gene":
				CenterGene=a
			elif o=="--normalize-gene":
				NormalizeGene=True
			elif o=="--prefix":
				prefix=a
			elif o=="--top-sd":
				topSD=int(a)
			elif o=='--top-cv':
				topCV=int(a)
			elif o=='--ignore-NA-rows':
				#ignoreNARows=True
				filledThreshold=1
			elif o=='--filled-threshold':
				filledThreshold=float(a)
			elif o=='--sd-threshold':
				SDThreshold=float(a)
			elif o=='--cv-threshold':
				CVThreshold=float(a)
			elif o=='--at-least-x-data-with-abs-val-ge-y':
				try:
					x,y=a.split(",")
					atLeastXDataWithAbsValGEY=[int(x),float(y)]
				except:
					print >> stderr,"incorrect format for this option, got",v,".Use --at-least-x-data-with-abs-val-ge-y x:int,y:float"
					printUsageAndExit(programName)
			elif o=='--max-min':
				maxMin=float(a)
			elif o in ["-p","--attach-param"]:
				attachParam=True
			elif o in ['-f','--folder']:
				folder=a
			elif o in ['--copy-array-tree-for-orig']:
				copyArrayTreeForOrig=True
			elif o in ['--out-pvalue-matrix']:
				pvalueMatrix=True
			elif o in ['--out-processed-data']:
				outProcessedData=True
				
	except:
		printUsage(programName)
		sys.exit()

	if attachParam:
		attachParam=[]
		
		if logbase!=0:
			attachParam.append("log"+logbaseDisplay)
		if filledThreshold!=0:
			attachParam.append("filled"+str(filledThreshold))
		if atLeastXDataWithAbsValGEY[0]!=0:
			attachParam.append(str(atLeastXDataWithAbsValGEY[0])+"ptGE"+str(atLeastXDataWithAbsValGEY[1]))
		if topSD!=0:
			attachParam.append("topsd"+str(topSD))
		if topCV!=0:
			attachParam.append("topcv"+str(topCV))  
		if SDThreshold!=0:
			attachParam.append("sdt"+str(SDThreshold))
		if CVThreshold!=0:
			attachParam.append("cvt"+str(CVThreshold))
		if CenterGene!="":
			attachParam.append("cg"+CenterGene)
		if NormalizeGene:
			attachParam.append("ng")
		attachParam.append(distance+clustermethod)
		jobname+="."+".".join(attachParam)
		
	if folder!="":
		jobname=folder+"/"+jobname
		
	absfolder=dirname(jobname)
	if absfolder!="" and not exists(absfolder):
		print >> stderr,"jobname:",jobname
		print >> stderr,"folder",absfolder,"does not exist. mkdir"
		mkdir(absfolder)

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
				sd=numpy.std(nonmasked)
				if sd<SDThreshold:
					continue #SD Threshold not passed

			
			if CVThreshold>0.0:
				sd=numpy.std(nonmasked)
				absmean=abs(numpy.mean(nonmasked))
				CV=sd/absmean
				if CV<CVThreshold:
					continue #CV Threshold not passed
			
				
			
			logTransformInPlace(tM,Msk,logbase)
			M.append(tM)
			MASK.append(Msk)



	fil.close()	
	print >> stderr,"done reading"

	if topSD>0:
		Genes,M,MASK=topSDSubM(Genes,M,MASK,topSD)	
	
	if topCV>0:
		Genes,M,MASK=topCVSubM(Genes,M,MASK,topCV)	
	

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
	record.data=numpy.array(M)
	record.mask=numpy.array(MASK)
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
	#record.data=from2DArrayToTupleMap(data)
	#record.mask=from2DArrayToTupleMap(MASK)
	record.save(jobname,expclusters=ArrayTree)
	#biopython_cluster_savedata(jobname,expclusters=ArrayTree)


	if outProcessedData:
		fildata=open(jobname+".processed_matrix","w")
		filmask=open(jobname+".processed_mask","w")
		
		print >> fildata,"\t".join([UNIQID]+Arrays)
		print >> filmask,"\t".join([UNIQID]+Arrays)
		
		for geneName,datarow,maskrow in zip(Genes,M,MASK):
			print >> fildata,"\t".join([geneName]+toStrList(datarow))
			print >> filmask,"\t".join([geneName]+toStrList(maskrow))
		fildata.close()
		filmask.close()


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
	#also copy the array tree data to orig
	if copyArrayTreeForOrig:
		shutil.copyfile(jobname+".atr", jobname+"_orig.atr")
	
	#now rewrite

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=rearrangeColAndRowSqMatrix(ComArrayMatrix,findIndices(arrayOrdered,Arrays))
	
	for i in range(0,len(arrayOrdered)): #row
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)): #col
			if NALowerLeft and i>=j:
				print >> fil, "\t"+"NA",
			elif NAUpperRight and j>=i:
				print >> fil, "\t"+"NA",
			else:
				print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()
	
	
	
	if pvalueMatrix:
		Mt,MtRow,MtCol=matrix_transpose(M,len(M),len(M[0]))
		Maskt,MasktRow,MasktCol=matrix_transpose(MASK,len(MASK),len(MASK[0]))
		pvalueM=[]
		for i in range(0,MtRow):
			pvalueMRow=[]
			pvalueM.append(pvalueMRow)
			for j in range(0,MtRow):
				#if j<i:
					#pvalueMRow.append("NA")
				if j==i:
					pvalueMRow.append(1.0)
				else:
					Mi,Mj=getNonMaskedRowValuePairs(Mt[i],Maskt[i],Mt[j],Maskt[j])
					if distance=="c":
						cor,pvalue=pearsonr(Mi,Mj)
					elif distance=="s":
						cor,pvalue=spearmanr(Mi,Mj)
					else:
						print >> stderr,"pvalue matrix not supported for distance method",distance
					
					pvalueMRow.append(getSign(cor)*(1-pvalue))
		
		rearrangedpvalueM=rearrangeColAndRowSqMatrix(pvalueM,findIndices(arrayOrdered,Arrays))
		
		#now output
		fil=open(jobname+"_pvalueM.cdt","w")
		shutil.copyfile(jobname+".atr", jobname+"_pvalueM.atr")
		
		for lin in firstthreelines:
			print >> fil, lin
			
		for i in range(0,len(arrayOrdered)): #row
			print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
			for j in range(0,len(arrayOrdered)): #col
				if NALowerLeft and i>=j:
					print >> fil, "\t"+"NA",
				elif NAUpperRight and j>=i:
					print >> fil, "\t"+"NA",
				else:
					print >> fil,"\t"+str(rearrangedpvalueM[i][j]),
	
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


		
