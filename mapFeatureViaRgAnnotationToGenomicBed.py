#!/usr/bin/python

from sys import *
from getopt import getopt
from albertcommon import *

'''
[AceView.ncbi_36.pfamhits]>colStat.py ../../other_annos/acembly.rg
[:::::                  R 1                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       -1
2                       B                       notiri.bApr07
3                       C                       chr1
4                       D                       +
5                       E                       1717
6                       F                       3502
7                       G                       2052
8                       H                       3122
9                       I                       3
10                      J                       1717,2475,3083,
11                      K                       2090,2584,3502, 
12                      L                       0 
13                      M                       notiri
14                      N                       cmpl 
15                      O                       cmpl 
16                      P                       0,2,0,

[AceView.ncbi_36.pfamhits]>colStat.py -r1,2 x1.pfamhits.1.dequote 
[:::::                  R 1                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       # Gene  
2                       B                       Chromo  
3                       C                       gene  
4                       D                       end  
5                       E                       product  
6                       F                       pfam  
7                       G                       accession 
8                       H                       score  
9                       I                       from  
10                      J                       to (bp) 
11                      K                       matching  
12                      L                       to (AA) 
13                      M                       Expect
[:::::                  R 2                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       7tm_1.13
2                       B                       1
3                       C                       245963249
4                       D                       245953691
5                       E                       7tm_1.13.aApr07
6                       F                       7tm_1
7                       G                       PF00001.11
8                       H                       21.75
9                       I                       115
10                      J                       258
11                      K                       1
12                      L                       49
13                      M                       1.52575e-07


'''


def strV2IntWithTransform(L,t):
	newL=[]
	for i in range(0,len(L)):
		try:		
			newV=int(L[i])+t
			newL.append(newV)		
		except:
			pass

	return newL

def toStrArray(L):
	newL=[]
	for x in L:
		newL.append(str(x))
	
	return newL

def readRefGeneFormattedTable(fileRg,rgStartBase,rgEndBase,rgIdCol,rgChromCol,rgTxStartCol,rgTxEndCol,rgStrandCol,rgCDSStartCol,rgCDSEndCol,rgExonStartsCol,rgExonEndsCol,extraIncludeSource,extraIncludeKeys,extraIncludeCols):
	geneTable=dict()
	
	colKeysRequested=[]
	
	for source,key,col in zip(extraIncludeSource,extraIncludeKeys,extraIncludeCols):
		if not source: #means rg table
			colKeysRequested.append((col,key))

	fil=open(fileRg)
	for lin in fil:
		fields=lin.strip().split("\t")

		chrom=fields[rgChromCol]

		gtxStart0=int(fields[rgTxStartCol])-rgStartBase
		gtxEnd1=int(fields[rgTxEndCol])-rgEndBase+1
		gCDSStart0=int(fields[rgCDSStartCol])-rgStartBase
		gCDSEnd1=int(fields[rgCDSEndCol])-rgEndBase+1
		strand=fields[rgStrandCol]

		gExonStarts0=fields[rgExonStartsCol].strip(",").split(",")
		gExonEnds1=fields[rgExonEndsCol].strip(",").split(",")
		ID=fields[rgIdCol]
		

		gExonStarts0=strV2IntWithTransform(gExonStarts0,-rgStartBase)
		gExonEnds1=strV2IntWithTransform(gExonEnds1,-rgEndBase+1)		

		lengthg5UTR=0
		lengthg3UTR=0

		#lengthg5UTRSet=False
		#lengthg3UTRSet=False

		keyvaluepairs=dict()
		
		for col,key in colKeysRequested:
			keyvaluepairs[key]=fields[col]

	
		exonLengths=[]
		exonRelStarts0=[]		
		
		curRelStart0=0

		totalmRNALength=0

		for gExonStart,gExonEnd in zip(gExonStarts0,gExonEnds1):
			length=gExonEnd-gExonStart
			exonLengths.append(length)			
			exonRelStarts0.append(curRelStart0)
			curRelStart0+=length  #affects next exon
			totalmRNALength+=length
			
			if gCDSStart0>gExonStart: #both in 0, if gCDSStart0==gExonStart, means the exon starts off directly in CDS, contribution would be 0
				lengthg5UTR+=min(length,gCDSStart0-gExonStart) #both in 0-based, so add 1, but then discount 1
		
			if gExonEnd>gCDSEnd1: #both in 1. If gCDSEnd1==gExonEnd, means the exon starts off directly in CDS, contribution would be 0
				lengthg3UTR+=min(length,gExonEnd-gCDSEnd1) #both in 1-based, so add 1, so add 1, but then discount 1

		geneTable[ID]=[chrom,gtxStart0,gtxEnd1,strand,gCDSStart0,gCDSEnd1,totalmRNALength,lengthg5UTR,lengthg3UTR,exonRelStarts0,exonLengths,gExonStarts0,gExonEnds1,keyvaluepairs]
	fil.close()

	return geneTable

#def translate_inner_forward_strand(chrom,gtxStart0,gtxEnd1,strand,gCDSStart0,gCDSEnd1,totalmRNALength,lengthg5UTR,lengthg3UTR,exonRelStarts0,exonLengths,gExonStarts0,gExonEnds1,keyvaluepairs,relPos0):



def translateRelToGenomicPositionAndExonIndex(geneRecord,relPos0,wasRelToCDS):
	chrom,gtxStart0,gtxEnd1,strand,gCDSStart0,gCDSEnd1,totalmRNALength,lengthg5UTR,lengthg3UTR,exonRelStarts0,exonLengths,gExonStarts0,gExonEnds1,keyvaluepairs=geneRecord #load gene record
	if strand=="+":
		#pos strand!
		if wasRelToCDS:
			relPos0+=lengthg5UTR #translate to rel-to-mRNA
		
	else: #strand not specified: assume negative strand
		if wasRelToCDS:
			relPos0+=lengthg3UTR #translate to rel-to-mRNA (still on negative strand)
		#now translate to positive strand
		relPos0=totalmRNALength-1-relPos0
		
	p=0
	
	if relPos0>=totalmRNALength:
		print >> stderr,relPos0
		raise KeyError

	while p<len(exonRelStarts0)-1 and relPos0>=exonRelStarts0[p+1]:
		p+=1

	exonRelStart0=exonRelStarts0[p]
	offset0=relPos0-exonRelStart0
	gcoord0=gExonStarts0[p]+offset0

	return [gcoord0,p,offset0]


def swapContentOfListsInPlace(L1,L2):
	if len(L1)!=len(L2):
		raise ValueError

	for i in range(0,len(L1)):
		v1=L1[i]
		L1[i]=L2[i]
		L2[i]=v1



def printUsageAndExit(programName):
	print >> stderr,programName,"[Options]","fileRg,fileFeatureMap,featureMapIdCol,featureStartCol,featureEndCol,featureMapFeatureNameCol".replace(","," ")
	print >> stderr,"[Options]"
	print >> stderr,"--rg-start-base x [ 0 ]"
	print >> stderr,"--rg-end-base x [ 1 ]"
	print >> stderr,"--rgIdCol x [ 2 ]"
	print >> stderr,"--rgChromCol x [ 3 ]"
	print >> stderr,"--rgTxStartCol x [ 5 ]"
	print >> stderr,"--rgTxEndCol x [ 6 ]"
	print >> stderr,"--rgStrandCol x [ 4 ]"
	print >> stderr,"--rgCDSStartCol x [ 7 ]"
	print >> stderr,"--rgCDSEndCol x [ 8 ]"
	print >> stderr,"--rgExonStartsCol x [ 10 ]"
	print >> stderr,"--rgExonEndsCol x [ 11 ]"
	print >> stderr,"--extra-rg-key keyname --with-col col"
	print >> stderr,"--extra-featuermap-key keyname --with-col col"
	print >> stderr,"--featuremap-start-base x [ 1 ]" 
	print >> stderr,"--featuremap-end-base x [ 1 ]"
	print >> stderr,"--relative-to-CDS-Bound [default: relative to mRNA bound]"
	print >> stderr,"--aa given is amino acide coordinate. start0=(aa*3) automatically turn on also relative-to-CDS-Bound"
	print >> stderr,"--block-format show individual blocks"
	print >> stderr,"--color color"
	print >> stderr,"--score scoreCol or 0 means use 0"
	print >> stderr,"--static-score f set static score"
	print >> stderr,"--score-col col set the score col from featuremap file"
	explainColumns(stderr)
	exit()

if __name__=='__main__':

	#fixed:
	headerRow=1
	fs="\t"
	blockFormat=False
	#settable options:
	rgStartBase=0
	rgEndBase=1
	rgIdCol = 2 - 1
	rgChromCol = 3 - 1 
	rgTxStartCol = 5 - 1
	rgTxEndCol = 6 - 1
	rgStrandCol = 4 - 1 
	rgCDSStartCol = 7 - 1
	rgCDSEndCol = 8 - 1
	rgExonStartsCol = 10 - 1
	rgExonEndsCol = 11 - 1 
	extraIncludeSource = [] #false => rg, true => featureMap
	extraIncludeKeys = []
	extraIncludeCols = []
	AA=False
	featureMapStartBase=1
	featureMapEndBase=1
	color="0,0,0"
	useScoreCol=False
	scoreParam=0.0
	relativeToCDS=False

	programName=argv[0]
	opts,args=getopt(argv[1:],'',['rgIdCol=','rg-start-base=','rg-end-base=','rgChromCol=','rgTxStartCol=','rgTxEndCol=','rgStrandCol=','rgCDSStartCol=','rgCDSEndCol=','rgExonStartsCol=','rgExonEndsCol=','extra-rg-key=','extra-featuremap-key=','with-col=','featuremap-start-base=','featuremap-end-base=','relative-to-CDS-Bound','block-format','aa','color=','score-col=','static-score='])



	try:
		fileRg,fileFeatureMap,featureMapIdCol,featureMapStartCol,featureMapEndCol,featureMapFeatureNameCol=args
	except:
		printUsageAndExit(programName)


	startRow=headerRow+1
	headerRg,prestarts=getHeader(fileRg,headerRow,startRow,fs)
	headerFeatureMap,prestarts=getHeader(fileFeatureMap,headerRow,startRow,fs)	
	
	for o,v in opts:
		if o=='--rgIdCol':
			rgIdCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rg-start-base':
			rgStartBase=int(v)
		elif o=='--rg-end-base':
			rgEndBase=int(v)
		elif o=='--rgChromCol':
			rgChromCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]	
		elif o=='--rgTxStartCol':
			rgTxStartCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]	
		elif o=='--rgTxEndCol':
			rgTxEndCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rgStrandCol':
			rgStrandCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rgCDSStartCol':
			rgCDSStartCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rgCDSEndCol':
			rgCDSEndCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rgExonStartsCol':
			rgExonStartsCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--rgExonEndsCol':
			rgExonEndsCol=getCol0ListFromCol1ListStringAdv(headerRg,v)[0]
		elif o=='--extra-rg-key':
			extraIncludeSource.append(False)
			extraIncludeKeys.append(v)
		elif o=='--extra-featuremap-key':
			extraIncludeSource.append(True)
			extraIncludeKeys.append(v)
		elif o=='--with-col':
			if extraIncludeSource[-1]:
				extraIncludeCols.append( getCol0ListFromCol1ListStringAdv(headerFeatureMap,v)[0] )
			else:			
				extraIncludeCols.append( getCol0ListFromCol1ListStringAdv(headerRg,v)[0] )
		elif o=='--featuremap-start-base':
			featureMapStartBase=int(v)
		elif o=='--featuremap-end-base':
			featureMapEndBase=int(v)
		elif o=='--relative-to-CDS-Bound':
			relativeToCDS=True
		elif o=='--aa':
			AA=True
			relativeToCDS=True
		elif o=='--block-format':
			blockFormat=True
		elif o=='--color':
			color=v
		elif o=='--static-score':
			useScoreCol=False
			scoreParam=float(v)
		elif o=='--score-col':
			useScoreCol=True
			scoreParam=getCol0ListFromCol1ListStringAdv(headerFeatureMap,v)[0]
		

	featureMapIdCol=getCol0ListFromCol1ListStringAdv(headerFeatureMap,featureMapIdCol)[0]
	featureMapStartCol=getCol0ListFromCol1ListStringAdv(headerFeatureMap,featureMapStartCol)[0]
	featureMapEndCol=getCol0ListFromCol1ListStringAdv(headerFeatureMap,featureMapEndCol)[0]
	featureMapFeatureNameCol=getCol0ListFromCol1ListStringAdv(headerFeatureMap,featureMapFeatureNameCol)[0]

	print >> stderr,"reading refGene Table from",fileRg
	geneTable=readRefGeneFormattedTable(fileRg,rgStartBase,rgEndBase,rgIdCol,rgChromCol,rgTxStartCol,rgTxEndCol,rgStrandCol,rgCDSStartCol,rgCDSEndCol,rgExonStartsCol,rgExonEndsCol,extraIncludeSource,extraIncludeKeys,extraIncludeCols)
	

	print >> stderr,"reading and processing feature map",fileFeatureMap
	#now go thru feature map
	fil=open(fileFeatureMap)
	lino=0
	for lin in fil:
		lino+=1		
		fields=lin.strip().split(fs)
		try:
			#read in
			featureId=fields[featureMapIdCol]
			try:
				geneRecord=geneTable[featureId]
			except:
				print >> stderr,"feature with gene ID",featureId,"not matched in gene table"
				continue  #ignore

			featureName=fields[featureMapFeatureNameCol]
			featureStart0=int(fields[featureMapStartCol])-featureMapStartBase #base-0 as well
			featureEnd0=int(fields[featureMapEndCol])-featureMapEndBase  #base-0 as well
			
			if useScoreCol:
				score=float(fields[scoreParam])
			else:
				score=scoreParam


			if AA:
				#was amino acid coordinate to convert to featureStart0 and featureEnd0, do *3
				featureStart0*=3
				featureEnd0*=3
			
		except:
			print >> stderr,"line",lino,"ignored [invalid formatting?]",lin.strip()
			continue

		#process and print
		#now find genomic coords

		#print >> stderr,geneRecord
		#print >> stderr,featureName,featureStart0,featureEnd0

		chrom,gtxStart0,gtxEnd1,strand,gCDSStart0,gCDSEnd1,totalmRNALength,lengthg5UTR,lengthg3UTR,exonRelStarts0,exonLengths,gExonStarts0,gExonEnds1,keyvaluepairs=geneRecord
					
		try:
			featureStartResult=translateRelToGenomicPositionAndExonIndex(geneRecord,featureStart0,relativeToCDS)
			featureEndResult=translateRelToGenomicPositionAndExonIndex(geneRecord,featureEnd0,relativeToCDS)
		except KeyError:
			print >> stderr,"strangeEntry:"
			print >> stderr,"strangeEntry\twith Gene Record",geneRecord
			print >> stderr,"strangeEntry\tand feature",featureId,featureName,featureStart0,featureEnd0
			continue #ignore
		
		if featureEndResult[0]<featureStartResult[0]: #comparing the starts		
			swapContentOfListsInPlace(featureStartResult,featureEndResult)

		featureStartGCoord0,featureStartP,featureStartOffset0=featureStartResult
		featureEndGCoord0,featureEndP,featureEndOffset0=featureEndResult

		featureEndGCoord1=featureEndGCoord0+1

		nameColValueOfBedFile=[featureName]
		
		#now go to the extra key value
		for source,key,col in zip(extraIncludeSource,extraIncludeKeys,extraIncludeCols):
			if source: #from feature map
				nameColValueOfBedFile.append(key+"="+fields[col])
			else: #from rg
				nameColValueOfBedFile.append(key+"="+keyvaluepairs[key])

		nameColValueOfBedFile="|".join(nameColValueOfBedFile)

		
		
		
		#print BED file
		if blockFormat:
			if featureStartP==featureEndP:  #start and end of feature on the same exon				
				print >> stdout,"\t".join([chrom,str(featureStartGCoord0),str(featureEndGCoord1),nameColValueOfBedFile,str(score),strand])
			else:	#not on the same exon
				print >> stdout,"\t".join([chrom,str(featureStartGCoord0),str(gExonEnds1[featureStartP]),nameColValueOfBedFile,str(score),strand])
				for p in range(featureStartP+1,featureEndP): #from the next one to the ending one (excluding)
					print >> stdout,"\t".join([chrom,str(gExonStarts0[p]),str(gExonEnds1[p]),nameColValueOfBedFile,str(score),strand])
				print >> stdout,"\t".join([chrom,str(gExonStarts0[featureEndP]),str(featureEndGCoord1),nameColValueOfBedFile,str(score),strand])
		else:
			toPrint=[chrom,str(featureStartGCoord0),str(featureEndGCoord1),nameColValueOfBedFile,str(score),strand,str(featureStartGCoord0),str(featureEndGCoord1),color]
			blockSizes=[]
			blockStarts=[]
			if featureStartP==featureEndP:
				blockSizes.append(featureEndGCoord1-featureStartGCoord0)
				blockStarts.append(0)
			else:
				blockSizes.append(gExonEnds1[featureStartP]-featureStartGCoord0)
				blockStarts.append(0)
				for p in range(featureStartP+1,featureEndP): #from the next one to the ending one (excluding)
					#print >> stdout,"\t".join([chrom,str(gExonStarts0[p]),str(gExonEnds1[p]),nameColValueOfBedFile,str(score),strand])
					blockSizes.append(gExonEnds1[p]-gExonStarts0[p])
					blockStarts.append(gExonStarts0[p]-featureStartGCoord0)
				blockSizes.append(featureEndGCoord1-gExonStarts0[featureEndP])
				blockStarts.append(gExonStarts0[featureEndP]-featureStartGCoord0)
			toPrint.append(str(len(blockSizes)))
			toPrint.append(",".join(toStrArray(blockSizes)))
			toPrint.append(",".join(toStrArray(blockStarts)))
			print >> stdout,"\t".join(toPrint)
			

	fil.close()
