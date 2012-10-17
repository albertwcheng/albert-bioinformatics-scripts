#!/usr/bin/env python

from sys import *
from albertcommon import *
from matrixTranspose import matrix_transpose
from getopt import getopt
from scipy.stats.stats import pearsonr,spearmanr
from os.path import basename

def printUsageAndExit(programName):
	print >> stderr,"%s [options] filename [grp1Label=]grp1Selector [grp2Label=]grp2Selector [ ... [grpNLabel=]grpNSelector ]" %(basename(programName))
	print >> stderr,"Options:"
	print >> stderr,"--method [*pearson|spearman]"
	print >> stderr,"--linkage [*average|single|complete]"
	exit(1)
	
#A[0]=A1[...]
#A[1]=A2[...]
#A[n]=An[...]

def single_linkage(A,B,distfunc):
	minDist=None		
	for a in A:
		for b in B:
			if minDist==None:
				minDist=distfunc(a,b)
			else:
				minDist=min(minDist,distfunc(a,b))
	
	return minDist
	
def complete_linkage(A,B,distfunc):
	maxDist=None
	for a in A:
		for b in B:
			if maxDist==None:
				maxDist=distfunc(a,b)
			else:
				maxDist=max(maxDist,distfunc(a,b))
	return maxDist
	
def average_linkage(A,B,distfunc):
	sumDist=0
	lenA=len(A)
	lenB=len(B)
	
	#print >> stderr,A
	#print >> stderr,B
	for a in A:
		for b in B:
			#print >> stderr,a,b
			sumDist+=distfunc(a,b)
	
	return 1.0/(lenA*lenB)*sumDist

def pearsonDist(a,b):
	return 1-pearsonr(a,b)[0]
	
def spearmanDist(a,b):
	return 1-spearmanr(a,b)[0]
	
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['method=','linkage='])
	
	groupLabelSelectors=[]
	
	try:
		filename=args[0]
		groupLabelSelectors=args[1:]
		if len(groupLabelSelectors)<2:
			print >> stderr,"less than two groups to compare, abort"
			raise Exception("less than two groups to compare")
		for i in range(0,len(groupLabelSelectors)):
			splits=groupLabelSelectors[i].split("=")
			if len(splits)>1:
				groupLabelSelectors[i]=[splits[0],splits[1]]
			else:
				groupLabelSelectors[i]=[splits[0],splits[0]]
		
			
	except:
		printUsageAndExit(programName)
	
	headerRow=1
	startRow=2
	fs="\t"
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	groupData=[]
	
	for i  in range(0,len(groupLabelSelectors)):
		groupLabelSelectors[i][1]=getCol0ListFromCol1ListStringAdv(header,groupLabelSelectors[i][1])
		groupData.append([])
		
	#grp1Selector=getCol0ListFromCol1ListStringAdv(header,grp1Selector)
	#grp2Selector=getCol0ListFromCol1ListStringAdv(header,grp2Selector)
	
	method=pearsonDist
	linkage=average_linkage
	
	for o,v in opts:
		if o=='--method':
			if v=="spearman":
				method=spearmanDist
			elif v=="pearson":
				method=pearsonDist
		elif o=='--linkage':
			if v=="average":
				linkage=average_linkage
			elif v=="complete":
				linkage=complete_linkage
			elif v=="single":
				linkage=single_linkage
		
	
	
	
	#StrListToFloatList(L)
	#selectListByIndexVector(L,I)
	fil=open(filename)
	lino=0
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		
		#A.append(StrListToFloatList(selectListByIndexVector(fields,grp1Selector)))
		#B.append(StrListToFloatList(selectListByIndexVector(fields,grp2Selector)))
		for groupDataMatrix,groupLabelSelector in zip(groupData,groupLabelSelectors):
			groupLabel,groupSelectors=groupLabelSelector
			groupDataMatrix.append(StrListToFloatList(selectListByIndexVector(fields,groupSelectors)))
		
	
	
	fil.close()
	
	#now transpose
	#A=matrix_transpose(A,len(A),len(A[0]))[0] #get the data only, discards the nrow and ncol
	#B=matrix_transpose(B,len(B),len(B[0]))[0] 
	for i in range(0,len(groupData)):
		groupData[i]=matrix_transpose(groupData[i],len(groupData[i]),len(groupData[i][0]))[0]
	
	
	#now calculate distance
	#dist=linkage(A,B,method)
	for i in range(0,len(groupLabelSelectors)):
		for j in range(i,len(groupLabelSelectors)):
			
			ALabel=groupLabelSelectors[i][0]
			BLabel=groupLabelSelectors[j][0]
			
			if i==j:
				print >> stdout,"%s\t%s\t%f" %(ALabel,BLabel,0.0)
				continue
				
			A=groupData[i]
			B=groupData[j]
			print >> stderr,"Calculate Distance Between",ALabel,"and",BLabel,
			dist=linkage(A,B,method)
			print >> stderr," dist=%f" %(dist)
			print >> stdout,"%s\t%s\t%f" %(ALabel,BLabel,dist)
	#print >> stdout,dist
	
	
	