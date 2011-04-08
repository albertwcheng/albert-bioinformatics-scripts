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

'''
extended bed (ebed)

1) chrom
2) chrom start g0
3) chrom end g1
4) name
5) score
6) strand
7) thickStart = CDS Start g0
8) thickEnd = CDS End g1
9) itemRGB
10) blockCount = exonCount
11) blockSizes (,)
12) blockStarts (,) relative to Chom Start in 0-based

----

genePred format

1) name
2) chrom
3) strand
4) txStart  g0
5) txEnd    g1
6) cdsStart  g0
7) cdsEnd    g1
8) exonCount  
9) exonStarts g0
10) exonEnds  g1

'''

from sys import *

''' 

these are in ebed2GenePred.py

def toStrListInPlaceRecursive(L,prefix="",suffix="",sep=",")

def ebedFields2genePredFields(fields,score,itemRgb,options)
	
def printListOfFields(stream,L,sep="\t")

'''

from ebed2GenePred import *		
	
#geneStruct["exon"][0]=[chrom,start,end,name]  #name can be just name (transcriptA) or add in feature name (transcriptA.exon1)
#geneStruct["cds"][0]
#geneStruct["intron"][0]
#geneStruct["5utr"]
#geneStruct["3utr"]
#geneStruct["utr"]

def getElementName(geneName,nameString,options):
	if options.IdFeatureSep:
		try:
			return geneName+options.IdFeatureSep+nameString
		except:
			print >> stderr,"error here"
			exit()
	else:
		return geneName

def idxSubStruct(L):
	for i in range(0,len(L)):
		idx=i+1
		#name fields is [3]
		L[i][3]+=str(idx)

def isBoundValid2(start0,end1):
	return start0>=0 and end1>=1 and end1>start0
	
def	isBoundValid(bound):
	return isBoundValid2(bound[0],bound[1])

def makeListOfTuples(listOfL):
	for i in range(0,len(listOfL)):
		listOfL[i]=tuple(listOfL[i])

def transcriptToGeneStruct(genePredFields,options):
	try:
		name,chrom,strand,txStartG0,txEndG1,cdsStartG0,cdsEndG1,exonCount,exonStartsG0,exonEndsG1=genePredFields
		txStartG0=int(txStartG0)
		txEndG1=int(txEndG1)
		cdsStartG0=int(cdsStartG0)
		cdsEndG1=int(cdsEndG1)
		exonCount=int(exonCount)
		exonStartsG0Splits=exonStartsG0.split(",")
		exonEndsG1Splits=exonEndsG1.split(",")
		exonStartsG0=[]
		for s in exonStartsG0Splits:
			s=s.strip()
			if len(s)>0:
				exonStartsG0.append(int(s))
		exonEndsG1=[]
		for s in exonEndsG1Splits:
			s=s.strip()
			if len(s)>0:
				exonEndsG1.append(int(s))
		
		if len(exonStartsG0)!=exonCount or len(exonEndsG1)!=exonCount:
			print >> stderr,"exon count not consistent with exon starts and exon ends data"
			raise ValueError
	
	except:
		print >> stderr,"format error",fields
		raise ValueError
	
	
	geneStruct=dict()
	#now initialize the gene struct
	exonStruct=[]
	cdsStruct=[]
	intronStruct=[]
	utrStruct=[]
	p5utrStruct=[] #for 5'utr can be composed by > 1 exon(s)
	p3utrStruct=[]
	
	geneStruct["exon"]=exonStruct
	geneStruct["cds"]=cdsStruct
	geneStruct["intron"]=intronStruct
	geneStruct["utr"]=utrStruct
	geneStruct["5utr"]=p5utrStruct
	geneStruct["3utr"]=p3utrStruct
	geneStruct["transcript"]=[chrom,txStartG0,txEndG1,name]
	geneStruct["strand"]=strand
	
	for idx,exonStartG0,exonEndG1 in zip(range(1,exonCount+1),exonStartsG0,exonEndsG1):
		if idx>1:
			newIntron=[chrom,prevExonEndG1,exonStartG0,getElementName(name,options.intronNameString,options)]
			intronStruct.append(newIntron)
		
		newExon=[chrom,exonStartG0,exonEndG1,getElementName(name,options.exonNameString,options)]	
		exonStruct.append(newExon)
		
		#now determine whether we are in utr, or coding region
		#if both cdsStartG0 and cdsEndG1 are valid:
		if cdsStartG0>=0 and cdsEndG1>=1 and cdsEndG1>cdsStartG0: #valid:
			leftPotentialUTRBound=[exonStartG0,min(exonEndG1,cdsStartG0)]
			potentialCDSBound=[max(exonStartG0,cdsStartG0),min(exonEndG1,cdsEndG1)]
			rightPotentialUTRBound=[max(cdsEndG1,exonStartG0),exonEndG1]
			
			if isBoundValid(leftPotentialUTRBound):
				newUTR=[chrom]+leftPotentialUTRBound+[getElementName(name,options.utrNameString,options)]
				utrStruct.append(newUTR)
				if strand=="-": #then it is a 3'UTR
					new3UTR=[chrom]+leftPotentialUTRBound+[getElementName(name,options.threeUTRNameString,options)]
					p3utrStruct.append(new3UTR)
				else:
					new5UTR=[chrom]+leftPotentialUTRBound+[getElementName(name,options.fiveUTRNameString,options)]
					p5utrStruct.append(new5UTR)
			
			if isBoundValid(potentialCDSBound):
				newCDS=[chrom]+potentialCDSBound+[getElementName(name,options.cdsNameString,options)]
				cdsStruct.append(newCDS)
			
			if isBoundValid(rightPotentialUTRBound):
				newUTR=[chrom]+rightPotentialUTRBound+[getElementName(name,options.utrNameString,options)]
				utrStruct.append(newUTR)
				if strand=="-":
					new5UTR=[chrom]+rightPotentialUTRBound+[getElementName(name,options.fiveUTRNameString,options)]
					p5utrStruct.append(new5UTR)
				else:
					new3UTR=[chrom]+rightPotentialUTRBound+[getElementName(name,options.threeUTRNameString,options)]
					p3utrStruct.append(new3UTR)
			
		else: #not valid, just put to utr, no coding region in this transcript
			newUTR=[chrom,exonStartG0,exonEndG1,getElementName(name,options.utrNameString,options)]
			utrStruct.append(newUTR)
		
		
		prevExonEndG1=exonEndG1
	
	if not options.genomicIndex and strand=="-":
		#filp the exon, cds, intron, utr lists if wanting transcript strand
		exonStruct.reverse()
		intronStruct.reverse()
		cdsStruct.reverse()
		utrStruct.reverse()
		p5utrStruct.reverse()
		p3utrStruct.reverse()
	
	if options.IdFeatureSep:
		#append also idx
		idxSubStruct(exonStruct)
		idxSubStruct(intronStruct)
		idxSubStruct(cdsStruct)
		idxSubStruct(utrStruct)
		idxSubStruct(p5utrStruct)
		idxSubStruct(p3utrStruct)
	
	makeListOfTuples(exonStruct)
	makeListOfTuples(intronStruct)
	makeListOfTuples(cdsStruct)
	makeListOfTuples(utrStruct)
	makeListOfTuples(p5utrStruct)
	makeListOfTuples(p3utrStruct)
	
	return geneStruct
	
def featureIdMatchParam(F,p):
	if F[:len(p)]==p:
		return F[len(p):]
	else:
		return None
		
def getStrArray(L):
	xL=[]
	for x in L:
		xL.append(str(x))
	return xL		
	
if __name__=='__main__':
	from optparse import OptionParser
	
	usage="""usage: %prog  [*--genePred|--ebed] [other options] inbed feature1 [feature2 ...] > outbed
feature list format:
transcript\ttranscription start to transcription stop of transcript
orf\ttranslation start to translation stop of transcript
5utr\t5' utr
3utr\t3' utr
cds\tcoding exons (coding regions of exons)
exon\texons
intron\tintrons
all\treturn all features
\tfor cds,exon,intron: You can indicate which ones by appending an index (from 1, in transcript strand). Can change to genomic strand by specifying --genomic-index
\t\te.g., exon1 gets the first exon (in transcript strand) or in genomic strand (if --genomic-index specified)
\t\te.g., exon-2 gets the second last exon (in transcript strand) or in genomic strand (if --genomic-index specified)
\t\te.g., exon2:-2 gets the seond exon to the second last exon

	"""
	
	parser=OptionParser(usage)
	
	parser.add_option("--genePred",dest="inFormat",default="genePred",action="store_const",const="genePred",help="input file is genePred format. Default is genePred")
	parser.add_option("--ebed",dest="inFormat",default="genePred",action="store_const",const="ebed",help="input file is ebed format")
	parser.add_option("--fs",dest="fs",default="\t",help="set input file field separate [tab]")
	parser.add_option("--genomic-index",dest="genomicIndex",default=False,action="store_true",help="index features by genomic strand")
	parser.add_option("--append-feature-to-id",dest="IdFeatureSep",default=None,help="<sep> turn on output of feature indicator to id, with separator. [default: off]")
	parser.add_option("--intron-name-string",dest="intronNameString",default="intron",help="set the name of an intron [intron]")
	parser.add_option("--exon-name-string",dest="exonNameString",default="exon",help="set the name of an exon [exon]")
	parser.add_option("--cds-name-string",dest="cdsNameString",default="cds",help="set the name of a cds [cds]")
	parser.add_option("--utr-name-string",dest="utrNameString",default="utr",help="set the name of an utr [utr]")
	parser.add_option("--5utr-name-string",dest="fiveUTRNameString",default="5utr",help="set the name of a 5' utr [5utr]")
	parser.add_option("--3utr-name-string",dest="threeUTRNameString",default="3utr",help="set the name of a 3' utr [3utr]")
	parser.add_option("--upstream-name-string",dest="upstreamNameString",default="upstream",help="set the name of an upstream region [upstream]")
	parser.add_option("--downstream-name-string",dest="downstreamNameString",default="downstream",help="set the name of a downstream region [downstream]")
		
	parser.add_option("--score",dest="bedScore",default="0",help="set score of the out bed [0]")
	
	(options,args)=parser.parse_args()
	
	try:	
		filename=args[0]
		featureList=args[1:]
		if len(featureList)<1:
			print >> stderr,"No feature supplied"
			raise KeyError
	except:
		parser.print_help()
		exit()
	
	
	for f in featureList:
		if f=="all":
			featureList=["exon","intron","cds","5utr","3utr","utr"]
			break
	
	#open file here:
	fil=open(filename)
	for lin in fil:
		fields=lin.rstrip("\r\n").split(options.fs)
		
		if options.inFormat=="genePred":
			pass #this is fine. No conversion needed
		elif options.inFormat=="ebed":
			#conversion
			try:
				fields=ebedFields2genePredFields(fields,0,"0,0,0",options)
			except:
				continue
				
		#get stuff into geneStruct
		#try:
		geneStruct=transcriptToGeneStruct(fields,options)
		#except:
		#	continue
			
		toOutputObjects=set()
		
		for feature in featureList:
			if feature=="transcript":
				toOutputObjects.add(tuple(geneStruct["transcript"]))
				continue
			
			if feature[:8]=="upstream":
				bp=int(feature[8:])
				chrom,txStartG0,txEndG1,name=geneStruct["transcript"]
				if not options.genomicIndex and geneStruct["strand"]=="-":
					#genomic downstream
					toOutputObjects.add((chrom,txEndG1,txEndG1+bp,getElementName(name,options.upstreamNameString+str(bp),options)))
				else:
					toOutputObjects.add((chrom,txStartG0-bp,txStartG0,getElementName(name,options.upstreamNameString+str(bp),options)))
				continue
				
			if feature[:10]=="downstream":
				bp=int(feature[10:])
				if not options.genomicIndex and geneStruct["strand"]=="-":
					#genomic upstream
					toOutputObjects.add((chrom,txStartG0-bp,txStartG0,getElementName(name,options.downstreamNameString+str(bp),options)))
				else:
					toOutputObjects.add((chrom,txEndG1,txEndG1+bp,getElementName(name,options.downstreamNameString+str(bp),options)))
				continue				
			
			for fKey in ["exon","intron","cds","utr","5utr","3utr"]:
				param=featureIdMatchParam(feature,fKey)
				if param!=None:
					#matched type request
					
					typeStruct=geneStruct[fKey]
					
					if len(param)>0:
						param=param.split(":")
						if len(param)==1:
							param=int(param[0])
							if param>=1:
								#this is from begining, to 0-based. if negative, ok no need to offset
								param-=1
							
							try:
								toOutputObjects.add(typeStruct[param])
							except:
								pass #out of bound
						elif len(param)==2:
							paramFrom=int(param[0])
							paramTo=int(param[1])
							if paramFrom<0: #firsrt convert to proper 0-based
								paramFrom=len(typeStruct)+paramFrom
							else:
								paramFrom-=1
								
							if paramTo<0:
								paramTo=len(typeStruct)+paramTo+1
								
							for k in range(paramFrom,paramTo):
								try:
									toOutputObjects.add(typeStruct[k])
								except:
									pass
							
						
						else:
							print >> stderr,"error: range specification error, use either x or x:y. seen:",param
					else:
						for elementData in typeStruct:
							toOutputObjects.add(elementData)
							
					break
		#now output:
		for o in toOutputObjects:
			printListOfFields(stdout,getStrArray(o+(options.bedScore,geneStruct["strand"])))
			
	fil.close()
	
	
