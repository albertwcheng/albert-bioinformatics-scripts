#!/usr/bin/env python

from numpy import *
from math import fabs,fsum
from scipy.stats import scoreatpercentile
from albertcommon import *
from sys import *
from optparse import OptionParser
from operator import itemgetter
from pvalue_module import *


def madAndMedian(X):
	med=median(X)
	abresidues=[]
	for x in X:
		abresidues.append(fabs(x-med))
	
	return median(abresidues),med

def standardizeGeneAcrossSamples(Xi,Mask,options):
	sX=[]
	sXUnMasked=[]
	
	XiUnMasked=getSubVectorByBinarySelector(Xi,Mask)
	
	madX,medX=madAndMedian(XiUnMasked)

	
	if madX==0.0 and options.addDeltaToMad>0.0:
		madX+=options.addDeltaToMad
	
	#print "XiUnMasked=",XiUnMasked
	#print "madX=",madX
	#print "medX=",medX
		
	for x,mask in zip(Xi,Mask):
		if mask==1:
			sx=(x-medX)/madX
			sX.append(sx)
			sXUnMasked.append(sx)
		else:
			sX.append("NA")
		
	
	
	return sX,sXUnMasked

def StringListToIntList(sL):
	IL=[]
	for s in sL:
		IL.append(int(s))
	return IL
	
def IQR(X):
	return scoreatpercentile(X,75)-scoreatpercentile(X,25)

def UpperOutlierLimit(X): #q75+IQR = 2*q75-q25
	return 2*scoreatpercentile(X,75)-scoreatpercentile(X,25)

def LowerOutlierLimit(X):
	return 2*scoreatpercentile(X,25)-scoreatpercentile(X,75)


#### These are for Outlier Sums described in Tibshirani et al, Biostatistics 8:1 pp 2-8 (2007)
def OutlierSumsUpperWion(Xi,Mask,options):
	#first standardize Xi
	sXi,sXUnMasked=standardizeGeneAcrossSamples(Xi,Mask,options)
	
	#now get upper outlier limit on the OK values
	UOL=UpperOutlierLimit(sXUnMasked)
	
	XiOn=[]
	
	#now go thru list of sXi, if sXij > UOL, then set XiOn(i,j)=sXij else set 0
	for sx,mask in zip(sXi,Mask):
		if mask==0 or sx<=UOL:
			XiOn.append(0.0)
		else:
			XiOn.append(sx)
	
	return XiOn

def OutlierSumsLowerWion(Xi,Mask,options):
	#first standardize Xi
	sXi,sXUnMasked=standardizeGeneAcrossSamples(Xi,Mask,options)
	
	#now get upper outlier limit on the OK values
	LOL=LowerOutlierLimit(sXUnMasked)
	
	XiOn=[]
	
	#now go thru list of sXi, if sXij > UOL, then set XiOn(i,j)=sXij else set 0
	for sx,mask in zip(sXi,Mask):
		if mask==0 or sx>=LOL:
			XiOn.append(0.0)
		else:
			XiOn.append(sx)
	
	return XiOn

def OutlierSumsUpperWionMatrix(Xi,Mask,options):
	sWionMatrix=[]
	
	for XiRow,MaskRow in zip(Xi,Mask):
		sWionMatrix.append(OutlierSumsUpperWion(XiRow,MaskRow,options))
	
	return sWionMatrix

def OutlierSumsLowerWionMatrix(Xi,Mask,options):
	sWionMatrix=[]
	
	for XiRow,MaskRow in zip(Xi,Mask):
		sWionMatrix.append(OutlierSumsLowerWion(XiRow,MaskRow,options))
	
	return sWionMatrix

def OutlierSumsTwoSidedWiStatistics(Xi,grouping):
	UpperWi=OutlierSumsUpperWiStatistics(Xi,grouping)
	LowerWi=OutlierSumsLowerWiStatistics(Xi,grouping)
	return max(UpperWi,LowerWi)

def testCombinations():
	X=list(argv[1])
	k=int(argv[2])
	idxV=None
	while True:
		combination,idxV=NextCombinationOn(X,k,idxV)
		if combination==None:
			break
		print >> stdout,"".join(combination)
		
	#combinations=findCombinations(list(argv[1]),int(argv[2]))
	#for combination in combinations:
	#	print >> stdout,"".join(combination)
	
	#print >> stdout,"total number of combinations=",len(combinations)
	
#####

###
def divideVectorByGrouping(Xi,Mask,grouping):
	G0=[]
	G1=[]
	for x,groupflag,mask in zip(Xi,grouping,Mask):
		if not mask:
			continue
			
		if groupflag:
			G1.append(x)
		else:
			G0.append(x)
	
	return G0,G1


def PPSTs1StatisticsOnRow(Xi,Mask,grouping,options): #A(Treatment)>B(Control)

	B,A=divideVectorByGrouping(Xi,Mask,grouping)
	
	
	q95B=scoreatpercentile(B,options.PPSTPercentile)
	q5A=scoreatpercentile(A,100-options.PPSTPercentile)
	
	s1=0
	
	for a in A:
		if a>q95B:
			s1+=1
	
	for b in B:
		if b<q5A:
			s1+=1
	
	return s1
	
def PPSTs2StatisticsOnRow(Xi,Mask,grouping,options):
	
	B,A=divideVectorByGrouping(Xi,Mask,grouping)
	
	q95A=scoreatpercentile(A,options.PPSTPercentile)
	q5B=scoreatpercentile(B,100-options.PPSTPercentile)
	
	s2=0
	
	for b in B:
		if b>q95A:
			s2+=1
		
	for a in A:
		if a<q5B:
			s2+=1
	
	return s2

def PPSTs3StatisticsOnRow(Xi,Mask,grouping,options):
	
	B,A=divideVectorByGrouping(Xi,Mask,grouping)
	
	q95B=scoreatpercentile(B,options.PPSTPercentile)
	q5B=scoreatpercentile(B,100-options.PPSTPercentile)
	
	s3=0
	
	for a in A:
		if a>q95B:
			s3+=1
		elif a<q5B:
			s3+=1
			
	return s3
	
def PPSTs4StatisticsOnRow(Xi,Mask,grouping,options):
	
	B,A=divideVectorByGrouping(Xi,Mask,grouping)
	
	q95A=scoreatpercentile(A,options.PPSTPercentile)
	q5A=scoreatpercentile(A,100-options.PPSTPercentile)
	
	s4=0
	
	for b in B:
		if b>q95A:
			s4+=1
		elif b<q5A:
			s4+=1
	
	return s4


def PPSTs1thru4StatisticsOnRow(Xi,Mask,grouping,options):
	B,A=divideVectorByGrouping(Xi,Mask,grouping)
	q95A=scoreatpercentile(A,options.PPSTPercentile)
	q5A=scoreatpercentile(A,100-options.PPSTPercentile)
	q95B=scoreatpercentile(B,options.PPSTPercentile)
	q5B=scoreatpercentile(B,100-options.PPSTPercentile)

	s1=0
	s2=0
	s3=0
	s4=0
	
	for a in A:
		if a>q95B:
			s1+=1
			
		if a<q5B:
			s2+=1
			s3+=1		
		elif a>q95B:
			s3+=1

				
			
	for b in B:
		if b<q5A:
			s1+=1	
			
		if b>q95A:
			s2+=1
			s4+=1
		elif b<q5A:
			s4+=1


	return s1,s2,s3,s4

###


def stringListToFloatListWithMask(sL):
	values=[]
	masks=[]
	for s in sL:
		try:
			f=float(s)
			values.append(f)
			masks.append(1)
		except ValueError:
			values.append("NA")
			masks.append(0)
	return values,masks

#return geneNames,sampleNames and Matrix, and Mask
def readMatrix(filename,FS="\t"):
	geneNames=[]
	sampleNames=[]
	M=[]
	Mask=[]
	
	fil=open(filename)
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		fields=lin.split(FS)
		if lino==1: #header, get sample names
			sampleNames=fields[1:]
			cornerString=fields[0]
		else:
			#values and gene names
			geneNames.append(fields[0])
			values,masks=stringListToFloatListWithMask(fields[1:])
			M.append(values)
			Mask.append(masks)

	return cornerString,geneNames,sampleNames,M,Mask

def sumUpperWiStatistics(UpperWionMatrix,grouping):
	WiStats=[]
	for WionRow in UpperWionMatrix:
		WiStats.append(fsum(getSubVectorByBinarySelector(WionRow,grouping)))
	
	return WiStats

def sumLowerWiStatistics(LowerWionMatrix,grouping):
	WiStats=[]
	for WionRow in LowerWionMatrix:
		WiStats.append(fsum(getSubVectorByBinarySelector(WionRow,grouping)))
	
	return WiStats

def sumBothSidedWiStatistics(UpperWionMatrix,LowerWionMatrix,grouping):
	WiStats=[]
	for LWionRow,UWionRow in zip(LowerWionMatrix,UpperWionMatrix):
		WiStats.append(max(fsum(getSubVectorByBinarySelector(LWionRow,grouping)),fsum(getSubVectorByBinarySelector(UWionRow,grouping))))
	
	return WiStats	

def falseVectorOfLength(l):
	V=[]
	for i in range(0,l):
		V.append(0)
	
	return V

def sumWiStatistics(UpperWionMatrix,LowerWionMatrix,grouping,options):
	if options.WiStatType=="Upper":
		return sumUpperWiStatistics(UpperWionMatrix,grouping)
	elif options.WiStatType=="Lower":
		return sumLowerWiStatistics(LowerWionMatrix,grouping)
	elif options.WiStatType=="BothSided":
		return sumBothSidedWiStatistics(UpperWionMatrix,LowerWionMatrix,grouping)

def runOutlierSumsStatistics(filename,grouping,options):
	cornerString,geneNames,sampleNames,Matrix,Mask=readMatrix(filename,options.fs)
	
	if options.addDelta>0.0:
		for Mrow,MaskRow in zip(Matrix,Mask):
			for i in range(0,len(Mrow)):
				if MaskRow[i]==1:
					Mrow[i]+=options.addDelta
	
	UpperWionMatrix=OutlierSumsUpperWionMatrix(Matrix,Mask,options)
	LowerWionMatrix=OutlierSumsLowerWionMatrix(Matrix,Mask,options)	
		
	#calculate Wi, and associate with row-number
	WiStats=sumWiStatistics(UpperWionMatrix,LowerWionMatrix,grouping,options)
	
	rowNumWiStats=[]
	PermFPAtWi=[]
	
	for i,WiStat in zip(range(0,len(WiStats)),WiStats):
		rowNumWiStats.append((i,WiStat))
		PermFPAtWi.append(0)
		
	#now sort descending on WiStat (second element)
	rowNumWiStats.sort(key=itemgetter(1),reverse=True)
	
	#k=numTreatment=sum(grouping) 
	numTreatments=sum(grouping)
	numSamples=len(grouping)
	
	Tidx=[]
	Cidx=[]
	for idx,treatmentMembership in zip(range(0,len(grouping)),grouping):
		if treatmentMembership:
			Tidx.append(idx)
		else:
			Cidx.append(idx)
	
	PermSampleIdx=Tidx+Cidx # X = 1,3,5,6 (treatment) +  2,4,7,8,9 (control)
	PermUseIdx=None
	
	#consume the first one which is the experimental setup
	PermTreatIdx,PermUseIdx=NextCombinationOn(PermSampleIdx,numTreatments,PermUseIdx)
	
	#now permut grouping
	IPerm=0
	
	permGrouping=grouping[:]
	
	history=set()
	
	while True:
		IPerm+=1
		if options.permutations>0 and IPerm>options.permutations:
			IPerm-=1
			break #enough!~
		if options.randomShuffleOnGrouping:
			if not randomShuffleNoRepeat(permGrouping,history):
				IPerm-=1
				break
		else:
			if options.randomChooseK:
				PermTreatIdx=advRandomChooseKNoRepeat(PermSampleIdx,numTreatments,history)
			else:
				PermTreatIdx,PermUseIdx=NextCombinationOn(PermSampleIdx,numTreatments,PermUseIdx)
			
			if PermTreatIdx==None:
				#no more permutation possible anyway
				IPerm-=1
				break
			#get all zero's
			permGrouping=falseVectorOfLength(numSamples)
			#now set 1 to the treatment elements:
			for PermT in PermTreatIdx:
				#print >> stderr,"PermT=",PermT
		
				permGrouping[PermT]=1
		
		if sum(permGrouping)!=numTreatments:
			print >> stderr,"bug sum(permgrouping)!=numTreatments"
			exit(1)
		
		print >> stderr,"operating on permutation number",IPerm,"".join(toStrList(permGrouping))
		#now recal Wi for this permutation
		ThisPermWiStats=sumWiStatistics(UpperWionMatrix,LowerWionMatrix,permGrouping,options)
		ThisPermWiStats.sort(reverse=True) #sort the Wi values so that the two-pointer iteration thing can happen.
	
		#now Wi and ThisPermWiStats each has one pointer, go down the slope..
		
		pThisPermWiStats=0
		
		for prowNumWiStats in range(0,len(rowNumWiStats)):
			# go down this perm wi stats if it is still bigger than the experimental wi stats
			while pThisPermWiStats<len(ThisPermWiStats) and rowNumWiStats[prowNumWiStats][1]<=ThisPermWiStats[pThisPermWiStats]:
				pThisPermWiStats+=1
			
			PermFPAtWi[prowNumWiStats]+=pThisPermWiStats
			
	#now IPerm is the number of permutations done
	#go down permFP and get averages by dividing with float(IPerm), and get FDR by dividing by the idx+1
	
	
	FDRs=[]
	AveFPAtWi=PermFPAtWi
	for i in range(0,len(rowNumWiStats)):
		AveFPAtWi[i]/=float(IPerm)
		FDR=AveFPAtWi[i]/(i+1)
		if not options.NoCeilFDR:
			FDR=min(1.0,FDR)
		FDRs.append(FDR)
	
	#now output..
	#first output cornerString and sample names
	outputV=[cornerString]+sampleNames+["Wi","AveFPAtWi","FDR"]
	print >> stdout,options.fs.join(outputV)
	
	#now go down the rowNumWiStats List
	for rowNumWi,Avefp,FDR in zip(rowNumWiStats,AveFPAtWi,FDRs):
		#get back the gene name and exp values
		rowNum,Wi=rowNumWi
		outputV=[geneNames[rowNum]]+toStrList(Matrix[rowNum]+[Wi,Avefp,FDR])
		print >> stdout,options.fs.join(outputV)


def getPPSTs1thrus4StatsOnMatrixAndMask(Matrix,Mask,grouping,options):
	s1Stats=[]
	s2Stats=[]
	s3Stats=[]
	s4Stats=[]
	
	for Mrow,MaskRow in zip(Matrix,Mask):
		s1,s2,s3,s4=PPSTs1thru4StatisticsOnRow(Mrow,MaskRow,grouping,options)
		s1Stats.append(s1)
		s2Stats.append(s2)
		s3Stats.append(s3)
		s4Stats.append(s4)
	
	return s1Stats,s2Stats,s3Stats,s4Stats
		
def runPPSTStatistics(filename,grouping,options):
	cornerString,geneNames,sampleNames,Matrix,Mask=readMatrix(filename,options.fs)
	
	if options.addDelta>0.0:
		for Mrow,MaskRow in zip(Matrix,Mask):
			for i in range(0,len(Mrow)):
				if MaskRow[i]==1:
					Mrow[i]+=options.addDelta
	
	s1Stats,s2Stats,s3Stats,s4Stats=getPPSTs1thrus4StatsOnMatrixAndMask(Matrix,Mask,grouping,options)
	
	#now permute
	numTreatments=sum(grouping)
	numSamples=len(grouping)
	
	Tidx=[]
	Cidx=[]
	for idx,treatmentMembership in zip(range(0,len(grouping)),grouping):
		if treatmentMembership:
			Tidx.append(idx)
		else:
			Cidx.append(idx)
	
	PermSampleIdx=Tidx+Cidx # X = 1,3,5,6 (treatment) +  2,4,7,8,9 (control)
	PermUseIdx=None
	
	#consume the first one which is the experimental setup
	PermTreatIdx,PermUseIdx=NextCombinationOn(PermSampleIdx,numTreatments,PermUseIdx)
	
	#now permut grouping
	IPerm=0
	
	permGrouping=grouping[:]
	
	history=set()
	
	s1P=[]
	s2P=[]
	s3P=[]
	s4P=[]
	
	for i in range(0,len(s1Stats)): #fill up the s*P vectors
		s1P.append(0)
		s2P.append(0)
		s3P.append(0)
		s4P.append(0)
	
	while True:
		IPerm+=1
		if options.permutations>0 and IPerm>options.permutations:
			IPerm-=1
			break #enough!~
		if options.randomShuffleOnGrouping:
			if not randomShuffleNoRepeat(permGrouping,history):
				IPerm-=1
				break
		else:
			if options.randomChooseK:
				PermTreatIdx=advRandomChooseKNoRepeat(PermSampleIdx,numTreatments,history)
			else:
				PermTreatIdx,PermUseIdx=NextCombinationOn(PermSampleIdx,numTreatments,PermUseIdx)
			
			if PermTreatIdx==None:
				#no more permutation possible anyway
				IPerm-=1
				break
			#get all zero's
			permGrouping=falseVectorOfLength(numSamples)
			#now set 1 to the treatment elements:
			for PermT in PermTreatIdx:
				#print >> stderr,"PermT=",PermT
		
				permGrouping[PermT]=1
		
		if sum(permGrouping)!=numTreatments:
			print >> stderr,"bug sum(permgrouping)!=numTreatments"
			exit(1)
		
		print >> stderr,"operating on permutation number",IPerm,"".join(toStrList(permGrouping))
		
		#now recal s1thru4 stats for this permutation
		#ThisPermWiStats=sumWiStatistics(UpperWionMatrix,LowerWionMatrix,permGrouping,options)
		thiss1Stats,thiss2Stats,thiss3Stats,thiss4Stats=getPPSTs1thrus4StatsOnMatrixAndMask(Matrix,Mask,permGrouping,options)
		
		for i in range(0,len(thiss1Stats)):
			if s1Stats[i]<=thiss1Stats[i]:
				s1P[i]+=1
			
			if s2Stats[i]<=thiss2Stats[i]:
				s2P[i]+=1
			
			if s3Stats[i]<=thiss3Stats[i]:
				s3P[i]+=1
			
			if s4Stats[i]<=thiss4Stats[i]:
				s4P[i]+=1
	
	#done permuting
	#now get pvalues for s1 thru s4
	
	for i in range(0,len(s1Stats)):
		s1P[i]/=float(IPerm)
		s2P[i]/=float(IPerm)
		s3P[i]/=float(IPerm)
		s4P[i]/=float(IPerm)
		
	#s*P are now the p-values, get FDRs
	s1FDR=getFDRfromPvalue(s1P)
	s2FDR=getFDRfromPvalue(s2P)
	s3FDR=getFDRfromPvalue(s3P)	
	s4FDR=getFDRfromPvalue(s4P)		
	
	
	#now we are ready to print~!~!
	
	outputV=[cornerString]+sampleNames+["s1","s2","s3","s4","s1.pvalue","s2.pvalue","s3.pvalue","s4.pvalue","s1.FDR","s2.FDR","s3.FDR","s4.FDR"]
	print >> stdout,options.fs.join(outputV)
	
	for geneName,expRow,s1,s2,s3,s4,s1p,s2p,s3p,s4p,s1f,s2f,s3f,s4f in zip(geneNames,Matrix,s1Stats,s2Stats,s3Stats,s4Stats,s1P,s2P,s3P,s4P,s1FDR,s2FDR,s3FDR,s4FDR):
		outputV=[geneName]+toStrList(expRow+[s1,s2,s3,s4,s1p,s2p,s3p,s4p,s1f,s2f,s3f,s4f])
		print >> stdout,options.fs.join(outputV)
	
	
	
def testRandomShuffle():
	L=list('abcde')
	history=set()
	#while randomShuffleNoRepeat(L,history):
	#	print >> stdout,L
	
	combination=randomChooseKNoRepeat(L,3,history)
	while combination!=None:
		print >> stdout,"".join(combination)
		combination=randomChooseKNoRepeat(L,3,history)
		
def printUsageAndExit(parser):
	parser.print_help()
	exit(1)


#outlierAnalysis.py --add-delta-to-mad 0.0001 --random-shuffle-on-grouping  --permutations 100000  ELGFPNeg.exp.txt `cat ELGFPPos.oscls` > ELGFPPos.OutlierSums.xls


if __name__=='__main__':

	#testRandomShuffle()
	#exit(0)


	#testCombinations()
	#print OutlierSumsUpperWion([3.5,4.2,0.3,5.5,"NA",2.1,0.1,0.05,"NA",4.4,5.5,10.4],[1,1,1,1,0,1,1,1,0,1,1,1])
	parser=OptionParser(usage = "usage: %prog [options] filename grouping[0=control,1=treatment] method[OutlierSums,PPST]")
	parser.add_option("--fs",dest="fs",default="\t",help="set field separator of input file")
	parser.add_option("--Wi-stat-type",dest="WiStatType",default="Upper",help="set stat type for Wi stat [Upper],Lower,BothSided")
	parser.add_option("--permutations",dest="permutations",default=0,type="int",help="nubmer of permutation [default:0=all permutations]")
	parser.add_option("--add-delta",dest="addDelta",default=0.0,type="float",help="add a small number to each input to avoid division-by-zero errors")
	parser.add_option("--add-delta-to-mad",dest="addDeltaToMad",default=0.0,type="float",help="add a small number to mad to avoid division-by-zero errors if mad == 0.0")
	parser.add_option("--random-choose-k",dest="randomChooseK",default=False,action="store_true",help="random choose K")
	parser.add_option("--random-shuffle-on-grouping",dest="randomShuffleOnGrouping",default=False,action="store_true",help="random shuffle directly on grouping. Default was to permute in order. recommend using this function if complete permutations impossible")
	parser.add_option("--no-ceil-FDR",dest="NoCeilFDR",default=False,action="store_true",help="let FDR to go over 1.0")
	parser.add_option("--PPST-percentile",dest="PPSTPercentile",default=95.0,type="float",help="set PPST percentile [default: 95.0]")
	
	(options, args) = parser.parse_args()
	
	try:
		filename,grouping,method=args
	except:
		printUsageAndExit(parser)
	
	grouping=StringListToIntList(list(grouping))
	
	if options.WiStatType not in ["Upper","Lower","BothSided"]:
		print >> stderr,"WiStatType",options.WiStatType,"not recognized"
		printUsageAndExit(parser)
	
	if method=="OutlierSums":
		runOutlierSumsStatistics(filename,grouping,options)
	elif method=="PPST":
		runPPSTStatistics(filename,grouping,options)
	else:
		print >> stderr,"method not recognized:",method