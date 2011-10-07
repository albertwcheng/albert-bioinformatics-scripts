#!/usr/bin/env python

from getopt import getopt
from albertcommon import *
from sys import *
from math import log,fsum

#sigma over i (weighti * Pi)
def sumProbDists(PM,weights):

	lenFirstPM=len(PM[0])
	
	for P in PM:
		if len(P)!=lenFirstPM:
			print >> stderr,"error: length of P's in PM not consistent. Abort"
			exit(1)
	
	summedP=[]
	for i in range(0,lenFirstPM):
		summed=0.0
		for w,P in zip(weights,PM):
			summed+=w*P[i]
		summedP.append(summed)
	
	return summedP
	
#logb=log(base)
def shannonEntropy(P,logb):
	E=0.0
	for p in P:
		if p<0:
			print >> stderr,"error: negative probability. Abort"
			exit(1)
		#if p==0: no need to do anything, ignore..	
		if p>0:
			E-=p*log(p) #in natural log

	return E/logb #in proper base


def kullBackLeiblerDivergence(P,Q,logb):
	d=0.0
	for p,q in zip(P,Q):
		if p>0:
			d+=p*(log(p)-log(q))  #in natural log
	
	return d/logb #in proper base
	

def JSDTwoP(P,Q,logb):
	M=sumProbDists([P,Q],[0.5,0.5])
	return (kullBackLeiblerDivergence(P,M,logb)+kullBackLeiblerDivergence(Q,M,logb))/2
	
def JSD(PM,weights,logb):
	M=sumProbDists(PM,weights)
	firstTerm=shannonEntropy(M,logb)
	secondTerm=0.0
	for w,P in zip(weights,PM):
		secondTerm+=w*shannonEntropy(P,logb)

	return firstTerm-secondTerm
	

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] infile [[groupName cols weight] ...]"
	print >> stderr,"weight=1/n to let the program to calculate the weight evenly or use comma separated list"
	print >> stderr,"Options:"
	print >> stderr,"--logbase x. default 2, i.e., in bits"
	print >> stderr,"--readGroupFile filename. read group def in file as rows of tab-delimited groupName cols weight"
	exit(1)




def testTwoPCaseAndExit():
	P=[0.5,0.3,0.2]
	Q=[0.2,0.7,0.1]
	
	logb=log(2)
	
	print >> stderr,"JSDTwoP=",JSDTwoP(P,Q,logb)
	print >> stderr,"JSD=",JSD([P,Q],[0.5,0.5],logb)
	
	
	exit(0)

#groupInfo will become [ [groupName,cols,weight,actualColsIdx,PM] ]
def readFilePMsIntoGroupInfo(filename,groupInfo):
	startRow=2
	headerRow=1
	fs="\t"
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	for groupI in range(0,len(groupInfo)):
		groupName,cols,weight=groupInfo[groupI]
		actualColsIdx=getCol0ListFromCol1ListStringAdv(header,cols)
		groupInfo[groupI].append(actualColsIdx)
		PM=[]
		#now init PM according to the number of cols
		for i in range(0,len(actualColsIdx)):
			PM.append([]) #empty Prob dist for appending later while reading file
			
		groupInfo[groupI].append(PM)
	
	#now read file
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue #no content on this row, skip
		
		fields=lin.split(fs)
		#now assume first col is geneName
		geneName=fields[0]
		
		#now go to each groupInfo, and append appropriate PMs
		for groupName,cols,weights,actualColsIdx,PM in groupInfo:
			thisAppend=[]
			hasNA=False
			for colIdx in actualColsIdx:
				try:
					thisValue=float(fields[colIdx])
					thisAppend.append(thisValue)
				except:
					#invalid value skip the whole row
					hasNA=True
					break
					
			if hasNA:
				print >> stderr,"line",lino,"with rowName",geneName,"for group",groupName,"discarded due to invalid value"
			else:
				#now we can append, grow each P in PM for one entry
				for P,appendee in zip(PM,thisAppend):
					P.append(appendee)
			
	fil.close()
	
#normalize element in P such that it sums to 1	
def normalizeP(P):
	PSum=float(fsum(P))
	for i in range(0,len(P)):
		P[i]/=PSum
	
				
if __name__=="__main__":

	#testTwoPCaseAndExit()
	


	programName=argv[0]
	opts,args=getopt(argv[1:],'',['logbase=','readGroupFile='])
	
	logb=log(2)
	readGroupFile=None
	
	for a,v in opts:
		if a=='--logbase':
			logb=log(float(v))
		elif a=='--readGroupFile':
			readGroupFile=v
	
	evenWeight=False
	
	unprocessedGroupInfo=[]
	
	groupInfo=[]
	
	if readGroupFile:
		fil=open(readGroupFile)
		for lin in fil:
			unprocessedGroupInfo.append(lin.rstrip("\r\n").split("\t"))
		fil.close()		
	
	try:
		infile=args[0]
	except:
		printUsageAndExit(programName)
		
	if (len(args)-1)%3!=0:
		print >> stderr,"invalid number of arguments. Abort"
		printUsageAndExit(programName)
	
	for i in range(1,len(args),3):
		unprocessedGroupInfo.append(args[i:i+3])
	
	for unprocessedGroupInfoEntry in unprocessedGroupInfo:
		groupName,cols,weight=unprocessedGroupInfoEntry
		
		
		
		if weight=="1/n":
			weight=None
		else:
			weight=weight.split(",")
			for i in range(0,len(weight)):
				weight=float(weight)
				#ensure weight sums to 1, normalize it.
			normalizeP(weight)
		
		groupInfo.append([groupName,cols,weight])
		
	

	
	#read file into PM
	readFilePMsIntoGroupInfo(infile,groupInfo)

	#numGroup=len(groupInfo)

	
	#now normalize PMs
	for thisGroupInfo in groupInfo:
	
		
		PM=thisGroupInfo[4]
		for P in PM:
			normalizeP(P)
			
		weight=thisGroupInfo[2]
		if not weight: #not specified, depends on the number of samples in group, set even weight
			numSamples=len(PM)
			weight=[1.0/numSamples]*numSamples
			thisGroupInfo[2]=weight
			
			
	#now it's ready for the math
	#for each group compute JSDivergence and output
	print >> stdout,"\t".join(["GroupName","ColSelector","ColSelected","Weights","JSD"])
	
	for groupName,cols,weights,actualColsIdx,PM in groupInfo:
		#print >> stderr,"calculating JSD for group",groupName,"..."
		jsd=JSD(PM,weights,logb)
		#now print
		print >> stdout,"\t".join([groupName,cols,",".join(toStrList(actualColsIdx)),",".join(toStrList(weights)),str(jsd)])
	
	
	#print >> stderr,"<Done>"