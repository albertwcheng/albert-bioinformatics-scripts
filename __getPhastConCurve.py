#!/usr/bin/python

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)


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

from sys import *
from getopt import getopt
from getOverlappingPiecesOfIntervals import *
from joinBedByOverlap import *
from scipy import *

def readPhastConFile_put(phastConBed,chrom,start1,values):
	length=len(values)
	if length<1:
		return

	#now empty values into phastConBed
	try:
		chromDict=phastConBed[chrom]
	except KeyError:
		chromDict=dict()
		phastConBed[chrom]=chromDict

	
	start0=start1-1
	end1=start0+length
	chromDict[(start0,end1)]=(values)

def makeVectorOfNANs(length):
	L=[]
	NAN=float('nan')
	for i in range(0,length):
		L.append(NAN)
	
	return L	

def toStrArray(F):
	S=[]
	for f in F:
		S.append(str(f))
	return S

def readPhastConFileIntoBed(filename):
	'''
	fixedStep chrom=chr11 start=3023589 step=1
	0.154
	0.219
	0.261
	0.289
	0.311
	0.319
	0.324
	0.325
	0.324
	0.316
	0.313
	base 1

	bed structure [chr] = chromDict[(start,end)]=[more]

	'''
	
	phastvalues=[]
	start1=-1000
	chrom=""

	phastConBed=dict()
	fil=open(filename)
	for lin in fil:
		fields=lin.rstrip().split(" ")
		if fields[0]=='fixedStep':
			readPhastConFile_put(phastConBed,chrom,start1,phastvalues)
			phastvalues=[]
			for field in fields[1:]:
				key,value=field.split("=")
				if key=='chrom':
					chrom=value
				elif key=='start':
					start1=int(value)

		else:
			phastvalues.append(float(fields[0]))

	
	#for the last bit
	readPhastConFile_put(phastConBed,chrom,start1,tuple(phastvalues))
	fil.close()
	return phastConBed
				
def isNaN(num):
	return num!=num		

def removeNANs(L):
	noNANs=[]
	for x in L:
		if not isNaN(x):
			noNANs.append(x)

	return noNANs
			

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['output-per-gene-infile','output-gene-level-matrix-to=',"output-gene-level-vector-to=",'phast-con-suffix=','bed-id-col='])
	

	outputPerGeneInFile=False
	outputGeneLevelMatrixTo=""
	outputGeneLevelVectorTo=""
	phastConSuffix=".data"
	bedIDCol=5
	binInterval=10000
	appenduplicate=False
	warnduplicate=False
	overlapLength=1
	addChromIfNeeded=True
	numFieldsInChromStartEnd=3
	ddofSD=1

	try:
		bedfile,phastConPrefix=args
	except:
		print >> stderr,programName,"[options] bedfile phastConPrefix > outputCurveFile"
		print >> stderr,"options:"
		print >> stderr,"--output-per-gene-infile   output the curve per gene into the curve file"
		print >> stderr,"--output-gene-level-vector-to <filename> output the per gene data as one column to filename"
		print >> stderr,"--output-gene-level-matrix-to <filename> output the per gene data as a matrix to filename"
		print >> stderr,"--phast-con-suffix <suffix>"
		print >> stderr,"--bed-id-col <col# in base 1> [=5]"
		exit()
	
	for o,v in opts:
		if o=='--output-per-gene-infile':
			outputPerGeneInFile=True
		elif o=='--output-gene-level-matrix-to':
			outputGeneLevelMatrix=v
		elif o=='--output-gene-level-vector-to':
			outputGeneLevelVector=v
		elif o=='--phast-con-suffix':
			phastConSuffix=v
		elif o=='--bed-id-col':
			bedIDCol=int(v)

	bedIDCol=bedIDCol-numFieldsInChromStartEnd-1 #chrom start end a b c enhID  => more=[a,b,c,endID] => to base 0   (indexed at 3 in "more" vector )
	startCol=2 - 1
	endCol=3 -1 	
	chrCol=1 -1 

	
	EnhPhastAllDict=dict()

	
	#now read in the bed file for enhancers
	print >> stderr, "reading in bed file"
	enhancerBed=readBed(bedfile,appenduplicate,warnduplicate)
	#now for each chrom in bed file, make a delegate subchrom bedfile
	for chrom,chromDict in enhancerBed.items():
		
		
		
		if chrom[:3]!="chr":
			chrom="chr"+chrom
		print >> stderr, "processing bed file chrom",chrom

		EnhPhastDict=dict()
		EnhPhastAllDict[chrom]=EnhPhastDict

		delegateEnhancerBed=dict()
		delegateEnhancerBed[chrom]=chromDict

		#now open the phast con file for that chrom
		phastConFileName=phastConPrefix+chrom+phastConSuffix

		print >> stderr,"reading in phastCon File into bed from",phastConFileName
		phastConBed=readPhastConFileIntoBed(phastConFileName)
		
		#now bin to speed up
		binDelegateEnhancerBed=binIntv(delegateEnhancerBed,binInterval)
		binPhastConBed=binIntv(phastConBed,binInterval)
		#now overlap those 
		#print >> stderr,"enhancerBed"
		#print >> stderr,delegateEnhancerBed

		#print >> stderr,"phastConBed"
		#print >> stderr,phastConBed
		jbed=joinIntervalsByBins(binDelegateEnhancerBed,binPhastConBed,delegateEnhancerBed,phastConBed,overlapLength,addChromIfNeeded,appenduplicate,warnduplicate,bedfile,phastConFileName)
		

		#print >> stderr,"jbed"
		#print >> stderr,jbed
		#the jbed structure
		#thisKey=(bin1Chr,coord1[0],coord1[1],coord2[0],coord2[1])
		#thisValue=(tuple(bed1ChromDict[coord1]),tuple(bed2ChromDict[coord2]),ob)

		
		#jbed is now holding whatever having the phast con data
		for thisKey,thisValue in jbed.items():
			#print >> stderr,"jbed.item",thisValue
			binChr,enhancerStart,enhancerEnd,phastStart,phastEnd=thisKey  #start in base-0, end in base-1
			enhancerMore,phastvalues,ob=list(thisValue)[0]
			#phastvalues=phastValuesHolder #stored in the 0-th cell
			#now 
			phastvaluesWantedI0=ob[0]-phastStart
			phastvaluesWantedI1=ob[1]-phastStart #exclusive
			phastvaluesWanted=phastvalues[phastvaluesWantedI0:phastvaluesWantedI1]
			
			LphastvaluesWanted=phastvaluesWantedI1-phastvaluesWantedI0

			lengthOfEnhancer=enhancerEnd-enhancerStart

			#enhID=enhancerMore[bedIDCol]
			enhKey=(enhancerStart,enhancerEnd)
			try:
				phastvaluesForThisEnhancer=EnhPhastDict[enhKey]
			except KeyError:
				phastvaluesForThisEnhancer=makeVectorOfNANs(lengthOfEnhancer)
				EnhPhastDict[enhKey]=phastvaluesForThisEnhancer
				
			for idxEnhPhastVector,phastvalueToSet in zip(range(ob[0]-enhancerStart,ob[0]-enhancerStart+LphastvaluesWanted),phastvaluesWanted):
				phastvaluesForThisEnhancer[idxEnhPhastVector]=phastvalueToSet

	print >> stderr,""
	#now we have this EnhPhastAllDict [chrom] = EnhPhastDict [(start,end)] = phastvalues
	#output phast score per enhancer
	for chrom,EnhPhastDict in EnhPhastAllDict.items():
		for coord,phastvalues in EnhPhastDict.items():
			maxScore=max(phastvalues)
			minScore=min(phastvalues)
			noNANs=removeNANs(phastvalues)
			meanScore=mean(noNANs)
			medianScore=median(noNANs)
			sdScore=std(noNANs,ddof=ddofSD)
			print >> stdout,"\t".join(toStrArray([chrom,coord[0],coord[1],maxScore,minScore,meanScore,medianScore]+phastvalues))
	
		
	
