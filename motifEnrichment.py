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


###############
#
#
# motifEnrichment.py
# find motif enriched in regions.
#
# To be used with Splidar output
# 
# Albert W. Cheng
# awcheng@mit.edu
# Updated 12/13/2009
# uses JHypergeometricPvalue for calculating hypergeometric pvalue instead
#
# Sequence tables are provided with a header, e.g., inFXseq
# Then each row in the column has first 2 chars as the element type, each separated by "|", e.g., I3ACAGAC|
#
# Enrichment results will be given per header per elementtype, e.g., inFXseq/I3
# 
# Two kinds of enrichment can be used
# Hypergeometric (-h) will be used to find motif enriched by hypergeometric word enrichment over background
# 1st order markov model (-1mm) will be used to find motif enriched over a 1st order markov model learned from mononucleotide and dinucleotide composition
# 
# Unbiased approach to identify all k-mers are available. Alternatively a targeted approach for identifying a motif family is provided (given the motif sequences or a  gapped alignment of the motif k-mers)
#
# A tool is also available for finding position of motifs.
#
#
#
###############


import warnings;
warnings.simplefilter('ignore', DeprecationWarning);

import shelve;
from clnum import *;
import sys;
from operator import itemgetter;
from sys import stdout;
from sys import stderr;
from sys import argv;
from scipy.stats.distributions import norm;
from math import sqrt;
from scipy.misc.common import comb
from random import randrange;
from random import randint
#import hypergeom;
#from hypergeom import pvalue_enrichment;
#from old_hypergeom import enrichment_pvalue;
from albertcommon import *
from getopt import getopt
from JHypergeometricPvalue import JHypergeometricPvalue
from ListPermuter import *

import scipy;
from math import floor;

def enrich_pvalue(m,mt,n,nt):
	pv=pvalue_enrichment(m,mt,n,nt);
	#if not ( pv>0 and pv<1):
	#	print >> sys.stderr, "pvalue_enrich using old version:",m,mt,n,nt;
	#	pv=enrichment_pvalue(m,mt,n,nt);
	return pv;


def Complement(c):
	if c=="C": return "G";
	elif c=="G": return "C";
	elif c=="T": return "A";
	elif c=="A": return "T";
	else: return "N";	

##def Reverse_Complementary(upperCaseSeq):
##	lenString=len(upperCaseSeq);
##	strResult="";	
##	for i in range(0,lenString):
##		strResult=Complement(upperCaseSeq[i])+strResult;
##
##	return strResult;



def sortedDictValues1(adict):
    items = adict.items()
    items.sort()
    return [value for key, value in items]


	


Nucleic=[];
Nucleic.append("A");
Nucleic.append("G");
Nucleic.append("C");
Nucleic.append("T");

NucleicD=dict();
for i in Nucleic:
	NucleicD[i]=1;

def hasN(seq):
	global Nucleic;

	lseq=len(seq);
	for i in range(0,lseq):
		if not NucleicD.has_key(seq[i]):
			return True;
	return False;



	

def hashSequenceSimple(element,content,N):

	global Nucleic;
	
	
	lcontent=len(content);
	end1=lcontent-N+1;

	
	countN=0;
	countNmers=0;


	wordFreq=element["wordFreq"];


	for i in range(0,end1):
		wordToHash=content[i:i+N];
		if hasN(wordToHash):
			continue;
		countNmers+=1;
		if wordFreq.has_key(wordToHash):
			wordFreq[wordToHash]+=1;
		else:
			wordFreq[wordToHash]=1;
	
	element["countNmers"]+=countNmers;

	return True;

def hashSequence1MM(element,content,eventID,N,CGBinKey,NmerList,noOverlap):

	global Nucleic;
	
	bins=element["bins"];

	if not bins.has_key(CGBinKey):
		CGBinned=dict();
		bins[CGBinKey]=CGBinned;
		model=dict();
		CGBinned["wordFreq"]=dict();
		CGBinned["model"]=model;
		CGBinned["countN"]=0;
		CGBinned["countNmers"]=0;
		CGBinned["CGValues"]=[];
		CGBinned["sequences"]=[];
		CGBinned["seqCGContent"]=[];
		for i in Nucleic:
			model["f"+i]=0;
			for j in Nucleic:
				model["f"+i+j]=0;

	else:
		CGBinned=bins[CGBinKey];
		model=CGBinned["model"];
	
	
	
	lcontent=len(content);
	end1=lcontent-N+1;

	
	countN=0;
	countNmers=0;

	for i in range(0,lcontent):
		char=content[i];
		j=i+1;
		if NucleicD.has_key(char):
			model["f"+char]+=1;
			countN+=1;
			if(j<lcontent):
				charj=content[j];
				if(NucleicD.has_key(charj)):
					model["f"+char+charj]+=1;			
		
	if(countN<1):
		return False;
	
	#now calculate C+G bin:
	#CGContent=float(model["fC"]+model["fG"])/countN;

	wordFreq=element["wordFreq"];
	wordPos=element["wordPos"]
	CGBinned["sequences"].append(content);

	block=dict()
		
	if len(NmerList)==0:	
		for i in range(0,end1):
			wordToHash=content[i:i+N];
			if hasN(wordToHash):
				continue;
		
			if not noOverlap:		
				countNmers+=1;

			if not block.has_key(wordToHash):
				block[wordToHash]=0

			if noOverlap and i<block[wordToHash]:
				continue
		
			posString=eventID+":"+str(i+1)
			
			if wordFreq.has_key(wordToHash):
				wordFreq[wordToHash]+=1;
				wordPos[wordToHash].append(posString)
			else:
				wordFreq[wordToHash]=1;
				wordPos[wordToHash]=[posString] #here

			
		
			if noOverlap:
				block[wordToHash]=i+N
	else:
		for i in range(0,end1):
			wordToHash=content[i:i+N];
			if hasN(wordToHash):
				continue;
		
			if not noOverlap:		
				countNmers+=1;
			
			for familyName,nmers in NmerList.items():
				if not block.has_key(familyName):
					block[familyName]=0

				if noOverlap and i<block[familyName]:
					continue
				
				for nmer in nmers:
					if wordToHash==nmer:

						posString=eventID+":"+str(i+1)

						if wordFreq.has_key(familyName):
							wordFreq[familyName]+=1;
							wordPos[wordToHash].append(posString)
						else:
							wordFreq[familyName]=1;
							wordPos[wordToHash]=[posString]
		
						if noOverlap:
							block[familyName]=i+N

						break

	
	if noOverlap:
		countNmers=lcontent/N

	CGBinned["countNmers"]+=countNmers;
	CGBinned["countN"]+=countN;
	element["countNmers"]+=countNmers;

	return True;


def binom_cdf(s, N, p):
	return scipy.special.betainc(N-floor(s), 1 + floor(s), 1-p)


def BinCDF_slow(_k,_l,_n,_p):
	k=mpf(_k);
	l=mpf(_l);
	n=mpf(_n);
	p=mpf(_p);

	cdf=mpf(0.0);
	q=1-p;
	for i in range(k,l+1):
		cdf+=binomial(n,i)*(p**i)*(q**(n-i));
	return [float(n*p),float(cdf)];

def DemoivreLaplaceApprox(k,l,n,p): #return [np, binP], not accurate
	np=float(n)*p;
	base=sqrt(np*(1-p));
	lf=float(l);
	kf=float(k);

	return [np,norm.cdf((lf+0.5-np)/base)-norm.cdf((kf-0.5-np)/base)];


def SeqProbOverAllBins(seq,CGBins): #get the probability of seq over the models in all bin weighted by Nmers
	if(len(seq)<1):
		return 0;
	
	bins=CGBins.values();
	Prob=0.0;	
	for bin in bins:
		Prob+=bin["weight"]*SeqProbFromModelPerCGBin(seq,bin["model"]);

	return Prob;
		

def SeqProbFromModelPerCGBin(seq,model): #get the probability of seq given the 1st order model in each bin
	lseq=len(seq);
	if(lseq<1):
		return 0;
	
	prob=model["p"+seq[0]];
	for i in range(1,lseq):
		prob*=model["p"+seq[i-1]+seq[i]];

	return prob;

def convertT2U(seq):
	return seq.replace("T","U");

def convertU2T(seq):
	return seq.replace("U","T");
	
def printModel(model):
	global Nucleic;
	
	print >> stderr,"event\t\tprobability";
	for i in Nucleic:
		print >>stderr, i,"\t\t",model["p"+i];
		for j in Nucleic:
			print >>stderr,i,">",j,"\t\t",model["p"+i+j];

def printSequences(CGBin):
	sequences=CGBin["sequences"];
	seqCGContents=CGBin["seqCGContent"];
	lseq=len(sequences);
	print >> stderr, "countN=",CGBin["countN"];
	print >> stderr, "countNmers=",CGBin["countNmers"];
	print >> stderr, "sequence\t\tCGContent";
	for i in range(0,lseq):
		print >> stderr, sequences[i],"\t\t",seqCGContents[i];

def finalize1MM(CGBin,parentElement):
	
	global Nucleic;

	
	model=CGBin["model"];
	countN=CGBin["countN"];
	countNmers=CGBin["countNmers"];	
	totalNmers=parentElement["countNmers"];
	CGBin["weight"]=float(countNmers)/totalNmers;

	for i in Nucleic:
		model["p"+i]=float(model["f"+i])/countN; #probability of the each nucleotide i
		for j in Nucleic:
			if(model["f"+i]==0):
				model["p"+i+j]=0;
			else:
				model["p"+i+j]=float(model["f"+i+j])/model["f"+i]; #transition probability of i->j


def calculatePValueNmerDict(element): #perElement
	
	global Nucleic;

	wordFreq=element["wordFreq"];
	wordKeys=wordFreq.keys();

	wordPos=element["wordPos"]
	
	pvalueWordMap=dict();
	element["pvalueWordMap"]=pvalueWordMap;
	CGBins=element["bins"];
	countNmers=element["countNmers"];


	for wordKey in wordKeys:
		pseq=SeqProbOverAllBins(wordKey,CGBins);
		obsFreq=wordFreq[wordKey];
		wordPosString="|".join(wordPos[wordKey])
		lowerBound=0;
		upperBound=obsFreq;
		print >>stderr, "cal Bin(l,k,n,p):",lowerBound,",",upperBound,",",countNmers,",",pseq, "word=", wordKey,
		expC=countNmers*pseq;
			
		np=expC;
		prob=binom_cdf(upperBound-1,countNmers,pseq);
		pvalue=1.0-prob;

		print >> stderr,": p-value=",pvalue;

		if not pvalueWordMap.has_key(pvalue):			
			pvalueWordMap[pvalue]=[];
			
		wordInfo=dict();
		wordInfo["wordKey"]=wordKey;
		wordInfo["expectedProb"]=pseq;
		wordInfo["expected"]=expC;
		wordInfo["observedProb"]=float(obsFreq)/countNmers;
		wordInfo["observed"]=obsFreq;
		wordInfo["wordPos"]=wordPosString
		
		pvalueWordMap[pvalue].append(wordInfo);

def commonPrefix(a,b):
	pref=""
	minl=min(len(a),len(b))
	for i in range(0,minl):
		if a[i]==b[i]:
			pref+=a[i]
		else:
			break

	return pref

def calculatePValueForNmerFam(element,NmerList): #perElement
	
	global Nucleic;

	wordFreq=element["wordFreq"];
	#wordKeys=wordFreq.keys();
	
	pvalueWordMap=dict();
	element["pvalueWordMap"]=pvalueWordMap;
	CGBins=element["bins"];
	countNmers=element["countNmers"];
	
	
	for FamilyName,Nmers in NmerList.items():
		pseq=0
		obsFreq=0
		
		for wordKey in Nmers:

			pseq+=SeqProbOverAllBins(wordKey,CGBins);

			#if not wordFreq.has_key(wordKey):
			#	continue
			
			#obsFreq+=wordFreq[wordKey];
		
		if not wordFreq.has_key(FamilyName):
			continue

		obsFreq=wordFreq[FamilyName]
	
		#correct for probability
		#for i in range(0,len(Nmers)-1):
		#	for j in range(i+1,len(Nmers)):
		#		intersectprob=SeqProbOverAllBins(commonPrefix(Nmers[i],Nmers[j]),CGBins);	
		##		intersectprob*=intersectprob
		#		pseq-=intersectprob
			
		lowerBound=0;
		upperBound=obsFreq;
		print >>stderr, "cal Bin(l,k,n,p):",lowerBound,",",upperBound,",",countNmers,",",pseq, "word=", FamilyName,
		expC=countNmers*pseq;
		np=expC;
		prob=binom_cdf(upperBound-1,countNmers,pseq);

		if obsFreq==0:
			pvalue=1.0
		else:
			pvalue=1.0-prob;
		if str(pvalue)=="nan":
			pvalue=1.0
		print >> stderr,": p-value=",pvalue;
	
		if not pvalueWordMap.has_key(pvalue):			
			pvalueWordMap[pvalue]=[];
				
		
		wordInfo=dict();
		wordInfo["wordKey"]=FamilyName;
		wordInfo["expectedProb"]=pseq;
		wordInfo["expected"]=expC;
		wordInfo["observedProb"]=float(obsFreq)/countNmers;
		wordInfo["observed"]=obsFreq;
		pvalueWordMap[pvalue].append(wordInfo);
					

def CGValue(seq):
	##print >> sys.stderr," getting CGValue:", seq;
	lseq=len(seq);
	CG=0;
	lreal=0;
	for i in range(0,lseq):
		if seq[i]=="C" or seq[i]=="G":
			CG+=1;
		elif seq[i]!="A" and seq[i]!="T":	
			continue;
		lreal+=1;

	if(lreal==0):
		print >> sys.stderr,"lreal=0, seq="+seq;
	return float(CG)/lreal;


def hashSequenceToCGBinByIntervals(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1,CGBinInterval):
	fin=open(filename);
	
	fromCol0=fromCol1-1;
	#strandCol0=strandCol1-1;

	header=[];

	lino=0;
	print >> stderr,"Hashing stuff..";
	for line in fin:
		lino+=1;
		line=line.strip();
		spliton=line.split("\t");
		if(lino==headerRow1):
			for i in range(fromCol0,toCol1):
				header.append(spliton[i]);
				DictNmer[spliton[i]]=dict();
		
		if(lino<startRow1):
			continue;
		
		for i in range(fromCol0,toCol1):
			key=header[i-fromCol0];
			#strand=spliton[strandCol0];
			content=spliton[i].upper();
			if(len(content)<3):
				continue;
	
			contentSplits=content.split("|");

			
			for contentSpliton in contentSplits:
				contentSpliton=contentSpliton.strip();
				if(len(contentSpliton)<3):
					continue;				
				elementKey=contentSpliton[0:2]; #first two chars are element
				elementSeq=contentSpliton[2:];
				
				
				##removed
				##if(strand=="-"):
				##### all sequences are in the sense direction
				##	elementSeq=Reverse_Complementary(elementSeq);
				####

				
				if not DictNmer[key].has_key(elementKey):
					perElement=dict();
					DictNmer[key][elementKey]=perElement;
					seqDict=dict();
					perElement["bins"]=dict();
					perElement["wordFreq"]=dict();
					perElement["countNmers"]=0;
					perElement["nseq"]=0;
					perElement["sequences"]=seqDict;
					perElement["bins"]=dict();
				else:
					perElement=DictNmer[key][elementKey];
				
				CGBins=perElement["bins"];
				CGVal=CGValue(elementSeq);
				CGBinKey=int(CGVal/CGBinInterval);
				if not CGBins.has_key(CGBinKey):
					CGBin=dict();
					CGBins[CGBinKey]=CGBin;
					CGBin["CGValues"]=[];
					CGBin["sequences"]=[];
					CGBin["nseq"]=0;
						#CGBinned["seqCGContent"]=[];
				else:
					CGBin=CGBins[CGBinKey];
				CGBin["sequences"].append(content);
				CGBin["CGValues"].append(CGVal);
				CGBin["nseq"]+=1;

	fin.close();	

def keySequenceByCGValue(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1,idCol0):

	#out:  DictNmer[header][element]["sequences"][CGValue]=[seq];
	#      DictNmer[header][element]["eventID"][CGValue]=[eventID];
	#      DictNmer[header][element]["nseq"]=number of sequences


	fin=open(filename);
	
	fromCol0=fromCol1-1;
	#strandCol0=strandCol1-1;

	header=[];

	lino=0;
	print >> stderr,"Hashing stuff..";
	for line in fin:
		lino+=1;
		line=line.strip();
		spliton=line.split("\t");
		if(lino==headerRow1):
			for i in range(fromCol0,toCol1):
				header.append(spliton[i]);
				DictNmer[spliton[i]]=dict();
		
		if(lino<startRow1):
			continue;
		
		eventID="#".join(getSubvector(spliton,idCol0))
		
		for i in range(fromCol0,toCol1):
			key=header[i-fromCol0];
			#strand=spliton[strandCol0];
			content=spliton[i].upper();
			if(len(content)<3):
				continue;
	
			contentSplits=content.split("|");

			
			for contentSpliton in contentSplits:
				contentSpliton=contentSpliton.strip();
				if(len(contentSpliton)<3):
					continue;				
				elementKey=contentSpliton[0:2]; #first two chars are element
				elementSeq=contentSpliton[2:];
				
				##if(strand=="-"):
#
				##	elementSeq=Reverse_Complementary(elementSeq);
				


				if not DictNmer[key].has_key(elementKey):
					DictNmer[key][elementKey]=dict();
					seqDict=dict();
					idDict=dict()
					DictNmer[key][elementKey]["wordFreq"]=dict();
					DictNmer[key][elementKey]["wordPos"]=dict();
					DictNmer[key][elementKey]["countNmers"]=0;
					DictNmer[key][elementKey]["nseq"]=0;
					DictNmer[key][elementKey]["sequences"]=seqDict;
					DictNmer[key][elementKey]["eventID"]=idDict;
					DictNmer[key][elementKey]["bins"]=dict();
				else:
					seqDict=DictNmer[key][elementKey]["sequences"];
					idDict=DictNmer[key][elementKey]["eventID"]
				
				CGval=CGValue(elementSeq);
				DictNmer[key][elementKey]["nseq"]+=1;
				if not seqDict.has_key(CGval):
					seqDict[CGval]=[];
					idDict[CGval]=[]
				seqDict[CGval].append(elementSeq);
				idDict[CGval].append(eventID)
	fin.close();


def getSimpleSequenceHash(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1):

	#out:  DictNmer[header][element]=[seq];



	fin=open(filename);
	
	fromCol0=fromCol1-1;
	#strandCol0=strandCol1-1;

	header=[];

	lino=0;
	print >> stderr,"Hashing stuff..";
	for line in fin:
		lino+=1;
		line=line.strip();
		spliton=line.split("\t");
		if(lino==headerRow1):
			for i in range(fromCol0,toCol1):
				header.append(spliton[i]);
				DictNmer[spliton[i]]=dict();
		
		if(lino<startRow1):
			continue;
		
		for i in range(fromCol0,toCol1):
			key=header[i-fromCol0];
			#strand=spliton[strandCol0];
			content=spliton[i].upper();
			if(len(content)<3):
				continue;
	
			contentSplits=content.split("|");

			
			for contentSpliton in contentSplits:
				contentSpliton=contentSpliton.strip();
				if(len(contentSpliton)<3):
					continue;				
				elementKey=contentSpliton[0:2]; #first two chars are element
				elementSeq=contentSpliton[2:];
				
				##if(strand=="-"):
#
				##	elementSeq=Reverse_Complementary(elementSeq);
				


				if not DictNmer[key].has_key(elementKey):

					seqList=[]
					DictNmer[key][elementKey]=seqList
				else:
					seqList=DictNmer[key][elementKey];


				seqList.append(elementSeq);
	fin.close();


def hashSequenceIntoBinByIntervals(DictNmer,N,CGInterval):

	#DictNmer[header][element]["bins"][CGBin]
	for header in DictNmer.keys():
		perHeader=DictNmer[header];
		for element in perHeader.keys():
			perElement=perHeader[element];
			CGV2Seq=perElement["sequences"];
			CGVals=CGV2Seq.keys();
			nSeqGroups=len(CGVals);
			nseq=perElement["nseq"];
			CGBins=perElement["bins"];
			CGBinKey=0;
			iseq=0;
			
			
			for CGVal in CGVals:
				CGBinKey=int(CGVal/CGInterval);
				sequencesToAdd=CGV2Seq[CGVal];
				for content in sequencesToAdd:
					#hashSequenceSimple(perElement,content,N);
					if not CGBins.has_key(CGBinKey):
						CGBin=dict();
						CGBins[CGBinKey]=CGBin;
						CGBin["CGValues"]=[];
						CGBin["sequences"]=[];
						#CGBinned["seqCGContent"]=[];
					else:
						CGBin=CGBins[CGBinKey];
					CGBin["sequences"].append(content);
					CGBin["CGValues"].append(CGVal);


def hashSequenceIntoBin(DictNmer,N,CGBinSize,NmerList,noOverlap):



	for header in DictNmer.keys():
		perHeader=DictNmer[header];
		for element in perHeader.keys():
			perElement=perHeader[element];
			CGV2Seq=perElement["sequences"];
			CGValSorted=sorted(CGV2Seq.keys());
			CGV2EventID=perElement["eventID"]
			nSeqGroups=len(CGValSorted);
			nseq=perElement["nseq"];
			CGBins=perElement["bins"];
			CGBinKey=0;
			iseq=0;
			while iseq<nSeqGroups:
				filled=0;

				if(nseq>CGBinSize):
					CGBinKey+=1;


				while iseq<nSeqGroups and filled<CGBinSize:
					CGVal=CGValSorted[iseq];
					sequencesToAdd=CGV2Seq[CGVal];
					eventIDToAdd=CGV2EventID[CGVal]
					lseq=len(sequencesToAdd);
					for content,eventID in zip(sequencesToAdd,eventIDToAdd):
						hashSequence1MM(perElement,content,eventID,N,CGBinKey,NmerList,noOverlap)
						CGBin=CGBins[CGBinKey];
						CGBin["CGValues"].append(CGVal);				
			
			

					nseq-=lseq;
					filled+=lseq;					
					iseq+=1;
			
			for bin in CGBins.values():
				finalize1MM(bin,perElement);
	

def buildModel1MM(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1,N,CGBinSize,NmerList,noOverlap,idCol0):
	#DictNmer[header][element]["nseq"]=number of sequences
	#DictNmer[header][element]["sequences"][CGValue]=[seq];
	#DictNmer[header][element]["eventID"][CGValue]=[eventID]
	#DictNmer[header][element]["pvalueWordMap"][pvalue]=[word];
	#DictNmer[header][element]["wordFreq"][word]=freq;
	#DictNmer[header][element]["countNmers"]=no. of Nmers possible
	
	#DictNmer[header][element]["bins"][CGBin]["weight"]=countNmers/total countNmers
	#DictNmer[header][element]["bins"][CGBin]["CGvalues"]=[CGValues];
	#DictNmer[header][element]["bins"][CGBin]["model"]["fA"]=freq of A
	#DictNmer[header][element]["bins"][CGBin]["model"]["fAC"]=freq of A -> C transition
	#DictNmer[header][element]["bins"][CGBin]["countNmers"]=no. of Nmers possible
	#DictNmer[header][element]["bins"][CGBin]["countN"]=no. of positions
	#DictNmer[header][element]["bins"][CGBin]["model"]["pA"]=probability of A
	#DictNmer[header][element]["bins"][CGBin]["model"]["pAC"]=probability of A -> C transition		
	keySequenceByCGValue(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1,idCol0);
	hashSequenceIntoBin(DictNmer,N,CGBinSize,NmerList,noOverlap);




def FDRCal(pvalueSorted,pvalueWordMap,numWords):
	m=0;
	FDRWordList=dict();

	for pvalue in pvalueSorted:
		wordList=pvalueWordMap[pvalue];
		m+=len(wordList);
		FDR=numWords*pvalue/m;
		if not FDRWordList.has_key(FDR):
			FDRWordList[FDR]=[];
		for wordInfo in wordList:
			wordInfo["p-value"]=pvalue;
			wordInfo["FDR"]=FDR;
			FDRWordList[FDR].append(wordInfo);
		
	return FDRWordList;




def constructHGWEProportionBGPerElement(FGElement,BGpElement,BGElement,N):
	#get the numbers of sequences in each bin
	FGBins=FGElement["bins"];
	BGpBins=BGpElement["bins"];
	
	
	BGBinRatio=[];

	for CGBinKey in FGBins:
		print >>sys.stderr,"getting bg/fg ratio for bin",CGBinKey,
		if not BGpBins.has_key(CGBinKey): #that specific bin is not found in bg set
			print >> sys.stderr,"CGBin",CGBinKey,"not found in background";
		else:
			CGBinBg=BGpBins[CGBinKey];
			CGBinFg=FGBins[CGBinKey];
			FgSequences=CGBinFg["sequences"];
			nCGBinBg=len(CGBinBg["sequences"]);
			nCGBinFg=len(FgSequences);
			
			for content in FgSequences: #include all foreground sequences;
				hashSequenceSimple(BGElement,content,N);
				hashSequenceSimple(FGElement,content,N);
			
			thisRatio=float(nCGBinBg)/nCGBinFg
			BGBinRatio.append(thisRatio);
			print >> sys.stderr, thisRatio;
			

	smallestRatio=min(BGBinRatio);
	print >> sys.stderr, "smallestRatio",smallestRatio;
	


	#now randomly choose background from each background bin

	for CGBinKey in FGBins:
		
		if BGpBins.has_key(CGBinKey):
			BgSequences=BGpBins[CGBinKey]["sequences"];
			nCGBinBg=len(BgSequences);
			nCGBinFg=len(FGBins[CGBinKey]["sequences"]);
			requiredNo=int(smallestRatio*nCGBinFg);
			if(requiredNo>nCGBinBg):
				print >> sys.stderr,"strange Error: required No > num there";
				exit();
			elif(requiredNo==nCGBinBg):
				for content in BgSequences:
					hashSequenceSimple(BGElement,content,N);
			else:
				for i in range(0,requiredNo):
					#randomly choose one in the background set.
					randi=randrange(0,nCGBinBg-i);
					#randi from Bg Sequences is chosen, copy it to BGElement,replace it by the nCGBinBg-i-1 element
					hashSequenceSimple(BGElement,BgSequences[randi],N);
					BgSequences[randi]=BgSequences[nCGBinBg-i-1];

def constructHGWEProportionBg(FG,BGp,BG,N):

	for header in FG.keys():
		##print >> sys.stdout, header+":";
		perHeaderFG=FG[header];
		perHeaderBGp=BGp[header];
		newBGPerHeader=dict();
		BG[header]=newBGPerHeader;

		for element in perHeaderFG.keys():
			##print >> sys.stdout, header+"."+element+":";
			perElementFG=perHeaderFG[element];
			perElementBGp=perHeaderBGp[element];
			
			perElementNewBG=dict();
			perElementNewBG["wordFreq"]=dict();
			perElementNewBG["countNmers"]=0;
			perElementNewBG["nseq"]=0;
			seqDict=dict();
			perElementNewBG["sequences"]=seqDict;
					


			newBGPerHeader[element]=perElementNewBG;
			
			constructHGWEProportionBGPerElement(perElementFG,perElementBGp,perElementNewBG,N);				
					

def toStrArray(L):
	sL=[]
	for l in L:
		sL.append(str(l))
	return sL
			
def findEnrichedMotifByHGWE(filenamefg,filenamebg,headerRow1,startRow1,fromCol1,toCol1,N,CGBinInterval,FDRCutOff,pvalueCutOff,topCount,NmerList):
	DictNmerFG=dict();
	DictNmerBGp=dict();
	DictNmerBG=dict();
	

	print >> sys.stderr,"put sequence into CG value bins";
	hashSequenceToCGBinByIntervals(DictNmerFG,filenamefg,headerRow1,startRow1,fromCol1,toCol1,CGBinInterval);
	hashSequenceToCGBinByIntervals(DictNmerBGp,filenamebg,headerRow1,startRow1,fromCol1,toCol1,CGBinInterval);

	print >> stdout,"header\telement\tp-value\tFDR\texpected rate\texpected freq\tobserved rate\tobserved freq\tword";
	

	#Now need to construct the real BG!
	print >> sys.stderr, "construct appropriate BG";
	constructHGWEProportionBg(DictNmerFG,DictNmerBGp,DictNmerBG,N);

	for header in DictNmerFG.keys():
		print >> sys.stderr, header+":";
		#print >> sys.stdout, header+":";
		perHeaderFG=DictNmerFG[header];
		perHeaderBG=DictNmerBG[header];

		for element in perHeaderFG.keys():
		
			#for each element
			
			#print >> sys.stderr, header+"."+element+":";
			print >> sys.stdout, header+"."+element+":";
			perElementFG=perHeaderFG[element];
			perElementBG=perHeaderBG[element];			
			
			#print >> sys.stderr, "output ",header+"."+element+":";

			wordFreqMapFG=perElementFG["wordFreq"];
			wordFreqMapBG=perElementBG["wordFreq"];
			numWordsFG=len(wordFreqMapFG);
			numWordsBG=len(wordFreqMapBG);
			#numWordsBGt=len(wordFreqMapBG);
			
			#total number of Nmers
			numNmersInCGBinFG=perElementFG["countNmers"];
			numNmersInCGBinBG=perElementBG["countNmers"];
			
			
			pvalueWordMap=dict();
			#remember for that header/element the pvalue->word map
			perElementFG["pvalueWordMap"]=pvalueWordMap;
				
			
			
			#changed to use JHypergeometricPvalue 12/13/2009
			
			JavaInputMatrix=[]	
			
			
			if len(NmerList)==0: #find all n-mers
				#the foreground word=>freq map					
				words=wordFreqMapFG.keys();
					
				#here, for each word in FG, calculate hypergeometric enrichment
				for word in words:
					freqFG=wordFreqMapFG[word];
					freqBG=wordFreqMapBG[word];
					
					#print >>stderr, word ,": Hypergeometric_cdf(m,mt,n,nt):",numNmersInCGBinBG,",",freqBG,",",numNmersInCGBinFG,",",freqFG,
					#pvalue=enrich_pvalue(numNmersInCGBinBG,freqBG,numNmersInCGBinFG,freqFG);
					#print >>stderr, word ," pvalue=",pvalue;
					#if not pvalueWordMap.has_key(pvalue):
					#	pvalueWordMap[pvalue]=[];
					#pvalueWordMap[pvalue].append({'p-value': pvalue, 'expectedProb': float(freqBG)/numNmersInCGBinBG, 'expected': freqBG, 'observedProb': float(freqFG)/numNmersInCGBinFG, 'observed': freqFG, 'wordKey': word});
					
					#samt,sam,popt,pop 
					JavaInputMatrix.append([freqFG,numNmersInCGBinFG,freqBG,numNmersInCGBinBG,word])	
			else: #find those in Nmerlist
				for FamilyName,Nmers in NmerList.items():
					freqFG=0
					freqBG=0
					for word in Nmers:
						freqFG+=wordFreqMapFG[word]
						freqBG+=wordFreqMapBG[word]
				
					JavaInputMatrix.append([freqFG,numNmersInCGBinFG,freqBG,numNmersInCGBinBG,FamilyName])
			
			JavaPvalues=JHypergeometricPvalue(JavaInputMatrix,-1)
			
			for inpu,pvalue in zip(words,JavaInputMatrix,JavaPvalues):
				freqFG,numNmersInCGBinFG,freqBG,numNmersInCGBinBG,word=inpu
				if not pvalueWordMap.has_key(pvalue):
					pvalueWordMap[pvalue]=[];
				pvalueWordMap[pvalue].append({'p-value': pvalue, 'expectedProb': float(freqBG)/numNmersInCGBinBG, 'expected': freqBG, 'observedProb': float(freqFG)/numNmersInCGBinFG, 'observed': freqFG, 'wordKey': word});	
				pseq+=SeqProbOverAllBins(wordKey,CGBins);
							
									
			pvalues=sorted(pvalueWordMap.keys());
			FDRWordMap=FDRCal(pvalues,pvalueWordMap,numWordsFG);
			FDRs=sorted(FDRWordMap.keys())
			outputed=0;
			#print >> stdout,"#NmersFG:",numNmersInCGBinFG,"#NmersBG:",numNmersInCGBinBG,"#wordsFG:",numWordsFG,"#wordsBG:",numWordsBG;
			#print >> stdout,"p-value\tFDR\texpected rate\texpected freq\tobserved rate\tobserved freq\tword";
			for pvalue in pvalues:
				
					
				if(pvalue>pvalueCutOff):
					break;		
			
				wordListWithThisPvalue=pvalueWordMap[pvalue];
				nWordWithThisPvalue=len(wordListWithThisPvalue);

				if(outputed+nWordWithThisPvalue>topCount and outputed>0):
					print >> stderr,"topCount cut-offed_:",outputed+nWordWithThisPvalue;
					break;
					#output!
					


				for wordInfo in wordListWithThisPvalue:
					#pvalue=wordInfo["p-value"];			
					FDR=wordInfo["FDR"];
					if(FDR>FDRCutOff):
						break;
					
					if len(NmerList)==0:
						wordInfoConv=convertT2U(wordInfo["wordKey"])
					else:
						wordInfoConv=wordInfo["wordKey"]
					print >>stdout, "\t".join(toStrArray([header,element,pvalue,FDR,wordInfo["expectedProb"],wordInfo["expected"],wordInfo["observedProb"],wordInfo["observed"],wordInfoConv]));
				
				outputed+=nWordWithThisPvalue;

				if(FDR>FDRCutOff):
					break;

				if(outputed>topCount):
					print >> stderr,"topCount cut-offed:",outputed;
			
		

def findEnrichedMotifBy1MM(filename,headerRow1,startRow1,fromCol1,toCol1,N,CGBinSize,FDRCutOff,pvalueCutOff,topCount,NmerList,noOverlap,idCol0):


	DictNmer=dict(); 

	buildModel1MM(DictNmer,filename,headerRow1,startRow1,fromCol1,toCol1,N,CGBinSize,NmerList,noOverlap,idCol0);
	
	print >> stdout,"Header\tElement\tp-value\tFDR\texpected rate\texpected freq\tobserved rate\tobserved freq\tword\tOccurences";
	
	print >> stderr,"Now cal enrichment and output..";	
	for header in DictNmer.keys():
		print >> sys.stderr, header,":";
		#print >> sys.stdout, header,":";
		perHeader=DictNmer[header];
		for element in perHeader.keys():
			print >> sys.stderr, header+"."+element+":";
			#print >> sys.stdout, header,".",element,":";
			perElement=perHeader[element];
			bins=perElement["bins"];
			totalNmers=perElement["countNmers"];
			numWords=len(perElement["wordFreq"]);
			for CGBinKey in bins.keys():

				CGBin=bins[CGBinKey];
				#printSequences(CGBin);
				model=CGBin["model"];
				countNmersBin=CGBin["countNmers"];
				numSeqs=len(CGBin["sequences"]);
				print >> sys.stderr, header,".",element,".bin[",CGBinKey,"] of CG [",CGBin["CGValues"][0],":",CGBin["CGValues"][len(CGBin["CGValues"])-1],"]";
				print >> sys.stderr,"numSeqs in bin=",numSeqs,",numNmers in bin=",countNmersBin,",numNmers total=",totalNmers, ",weight=",CGBin["weight"]
				
				printModel(model);
				#sort pvalue
				
			if len(NmerList)==0: 	
				calculatePValueNmerDict(perElement); #either calculate all k-mers present
			else:
				calculatePValueForNmerFam(perElement,NmerList) #or just the ones in the NmerList
			
			pvalueWordMap=perElement["pvalueWordMap"];

			pvalues=sorted(pvalueWordMap.keys());
			
			if len(NmerList)==0:
				numTests=numWords
			else:
				numTests=len(NmerList)
			
			FDRWordMap=FDRCal(pvalues,pvalueWordMap,numTests);
			FDRs=sorted(FDRWordMap.keys())
			outputed=0;
			#print >> stdout,"#Nmers:",totalNmers,"#words:",numWords;
			
			#print >> stdout,"p-value\tFDR\texpected rate\texpected freq\tobserved rate\tobserved freq\tword";
			
			for pvalue in pvalues:
				
					
				if(pvalueCutOff>=0 and pvalue>pvalueCutOff):
					print >> stderr,"pvalue cut-offed:",pvalue;
					break;		
			
				wordListWithThisPvalue=pvalueWordMap[pvalue];
				nWordWithThisPvalue=len(wordListWithThisPvalue);

				if(outputed+nWordWithThisPvalue>topCount and outputed>0):
					print >> stderr,"topCount cut-offed_:",outputed+nWordWithThisPvalue;
					break;
					#output!
					


				for wordInfo in wordListWithThisPvalue:
					#pvalue=wordInfo["p-value"];			
					FDR=wordInfo["FDR"];
					if(FDRCutOff>=0 and FDR>FDRCutOff):
						print >> stderr,"FDR cut-offed:",FDR;
						break;
						
					if len(NmerList)==0:
						wordInfoConv=convertT2U(wordInfo["wordKey"])
					else:
						wordInfoConv=wordInfo["wordKey"]
					print >>stdout, "\t".join(toStrArray([header,element,pvalue,FDR,wordInfo["expectedProb"],wordInfo["expected"],wordInfo["observedProb"],wordInfo["observed"],wordInfoConv,wordInfo["wordPos"]]))
					
					outputed+=nWordWithThisPvalue;

				if(FDRCutOff>=0 and FDR>FDRCutOff):
					print >> stderr,"FDR cut-offed:",FDR;
					break;

				if(outputed>topCount):
					print >> stderr,"topCount cut-offed:",outputed;


			
def findMotifPositions(filename,headerRow1,startRow1,chrCol1,eventIDCol1,geneCol1,coordCol1,fromCol1,toCol1,WordU):
	fin=open(filename);
	WordU=WordU.upper();
	Word=convertU2T(WordU);
	fromCol0=fromCol1-1;
	geneCol0=geneCol1-1;
	eventIDCol0=eventIDCol1-1;
	coordCol0=coordCol1-1;
	chrCol0=chrCol1-1;

	header=[];
	Occurences=dict();

	lino=0;
	print >> stderr,"Searching for motif occurences";
	for line in fin:
		lino+=1;
		line=line.strip();
		spliton=line.split("\t");
		if(lino==headerRow1):
			for i in range(fromCol0,toCol1):
				header.append(spliton[i]);
				Occurences[spliton[i]]=dict();
		
		if(lino<startRow1):
			continue;
		
		geneID=spliton[geneCol0];
		eventID=spliton[eventIDCol0];
		coord=spliton[coordCol0];
		chrom=spliton[chrCol0];
		
		for i in range(fromCol0,toCol1):
			key=header[i-fromCol0];
			content=spliton[i].upper();
			
			if(len(content)<3):
				continue;
	
			contentSplits=content.split("|");

			
			for contentSpliton in contentSplits:
				contentSpliton=contentSpliton.strip();
				if(len(contentSpliton)<3):
					continue;				
				elementKey=contentSpliton[0:2]; #first two chars are element
				elementSeq=contentSpliton[2:];
				
				##if(strand=="-"):
#
				##	elementSeq=Reverse_Complementary(elementSeq);
				


				if not Occurences[key].has_key(elementKey):
					Occurences[key][elementKey]=[];
				
				lenTarget=len(elementSeq);
				ThisPos=[];
				cur=0;
				try:
					while(True):
						index=elementSeq.index(Word,cur);
						cur=index+1;
						ThisPos.append(index);
				except ValueError:
					pass;
				
				freq=len(ThisPos);
				if(freq>0):
					#add to the record!
					Occurences[key][elementKey].append([chrom,geneID,eventID,coord,lenTarget,freq,ThisPos]);
				
				
	fin.close();
	for key in Occurences.keys():
		PerHeader=Occurences[key];
		for elementKey in PerHeader.keys():
			elementArray=PerHeader[elementKey];
			print >> stdout, key,".",elementKey,":"			
			print >> stdout, "Word\tChr\tGeneName\tEventID\tCoord\tLenTarget\tFreq\tPos";			
			for (chrom,geneID,eventID,coord,lenTarget,freq,ThisPos) in elementArray:
				print >> stdout, WordU+"\t"+chrom+"\t"+geneID+"\t"+eventID+"\t"+coord+"\t"+str(lenTarget)+"\t"+str(freq),
				for pos in ThisPos:
					print >> stdout, "\t"+str(pos),
				print >> stdout, "";



def getSubListByIndices(L,indices):
	sL=[]
	for index in indices:
		sL.append(L[index])

	return sL



def constructFactorialTable(FactTable,lower,upper):
	
	cur=1
	for i in range(lower,upper+1):
		if lower<=1:
			FactTable.append(1)
		else:
			cur*=i
			FactTable.append(cur)

	return FactTable

def initNmerAlignForShuffling(NmerAlign,gapMask,shufflerMatrix):
	
	#gapMask[family]=[true,true,false,false,...] #which position contains at least one gap
	#shufflerMatrix[family][alignI]=[permutations,..,...] #which position can be shuffled
	#factorials[i]=i! (from 0 to max length of align)
	
	maxAlignLength=0


	for familyName, aligns in NmerAlign.items():
		alignLength=len(aligns[0])
		maxAlignLength=max(maxAlignLength,alignLength)
		curGapMask=[]
		curShufflerMatrix=[]
		gapMask[familyName]=curGapMask
		shufflerMatrix[familyName]=curShufflerMatrix	
		for i in range(0,alignLength):
			curGapMask.append(False)		
		for align in aligns:
			for i in range(0,alignLength):
				if align[i]=='-':
					curGapMask[i]=True

		
		for align in aligns:
			shufflerMatrixLine=[]
			for g in range(0,alignLength):
				if not curGapMask[g]:
					shufflerMatrixLine.append(g)	
			
			#now constrcut permutation
			perm=getAllPermutationOfList(shufflerMatrixLine)
			curShufflerMatrix.append(perm)
		
			
	#constructFactorialTable(factorials,0,maxAlignLength)


#def randomizeInPlace(NmerAlign,)


AllAGTCPermutations=['AGTC', 'AGCT', 'ATGC', 'ATCG', 'ACGT', 'ACTG', 'CGTA', 'CGAT', 'CTGA', 'CTAG', 'CAGT', 'CATG', 'TGCA', 'TGAC', 'TCGA', 'TCAG', 'TAGC', 'TACG', 'GTCA', 'GTAC', 'GCTA', 'GCAT', 'GATC', 'GACT']
AGTCTranslatorMap={'A':0,'G':1,'T':2,'C':3}

#randint(0, 23)

def randomizeAlignMatrix(nmatrix):
	global AllAGTCPermutations,AGTCTranslatorMap
	lseq=len(nmatrix[0])
	nseq=len(nmatrix)
	#each of the position
	for c in range(0,lseq):
		#now choose a permutation scheme
		ran24=randint(0, 23)
		PermScheme=AllAGTCPermutations[ran24]
		for r in range(0,nseq):
			if nmatrix[r][c]!='-':
				#print >> stderr,nmatrix[r][c],PermScheme,AGTCTranslatorMap[nmatrix[r][c]]
	
				nmatrix[r]=nmatrix[r][:c]+PermScheme[AGTCTranslatorMap[nmatrix[r][c]]]+nmatrix[r][c+1:]

				
def findMotifFrequencyInSequence(seq,nmers,noOverlap):
	freq=0
	i=0
	lenTarget=len(seq)
	while(i<lenTarget):
		for nmer in nmers:
			lnmer=len(nmer)
			if seq[i:i+lnmer]==nmer: #match
				freq+=1
				if noOverlap:
					i+=lnmer-1
					break
							
		i+=1

	return freq

def findMotifFrequencyInSequences(seqs,nmers,noOverlap):
	freq=0
	for seq in seqs:
		freq+=findMotifFrequencyInSequence(seq,nmers,noOverlap)
	
	return freq

#findMotifPositions2(filename,headerRow1,startRow1,eventIDCols0,min(fromCol)+1,max(toCol)+1,NmerList,noOverlap)
def findMotifPositions2(filename,headerRow1,startRow1,eventIDCols0,fromCol1,toCol1,NmerList,noOverlap):
	fin=open(filename);
	#WordU=WordU.upper();
	#Word=convertU2T(WordU);
	fromCol0=fromCol1-1;
	#geneCol0=geneCol1-1;
	#eventIDCol0=eventIDCol1-1;
	#coordCol0=coordCol1-1;
	#chrCol0=chrCol1-1;

	header=[];
	Occurences=dict();
	#Occurences[Header][Element][familyName]	

	
	eventIDHeader=[]

	lino=0;
	print >> stderr,"Searching for motif occurences";
	for line in fin:
		lino+=1;
		line=line.strip();
		spliton=line.split("\t");
		if(lino==headerRow1):
			for i in range(fromCol0,toCol1):
				header.append(spliton[i]);
				Occurences[spliton[i]]=dict();

			eventIDHeader=getSubListByIndices(spliton,eventIDCols0)
			print >> stdout,"Header\tElement\t"+("\t".join(eventIDHeader))+"\tFamily\tFreq\tWord\tLenTarget\tPos"
		
		if(lino<startRow1):
			continue;
		
		eventIDOutput=getSubListByIndices(spliton,eventIDCols0)
		
		for i in range(fromCol0,toCol1):
			key=header[i-fromCol0];
			content=spliton[i].upper();
			
			if(len(content)<3):
				continue;
	
			contentSplits=content.split("|");

			
			for contentSpliton in contentSplits:
				contentSpliton=contentSpliton.strip();
				if(len(contentSpliton)<3):
					continue;				
				elementKey=contentSpliton[0:2]; #first two chars are element
				elementSeq=contentSpliton[2:];
				
				##if(strand=="-"):
#
				##	elementSeq=Reverse_Complementary(elementSeq);
				


				if not Occurences[key].has_key(elementKey):
					Occurences[key][elementKey]=dict();
				
				thisKeyElementDict=Occurences[key][elementKey]
				
				lenTarget=len(elementSeq);

				for familyName,nmers in NmerList.items():
					if not thisKeyElementDict.has_key(familyName):
						thisKeyElementDict[familyName]=[]
					
					
					thisRecord=thisKeyElementDict[familyName]		
					ThisPos=[];
					cur=0;
					
					#nmer is sorted by decreasing length
					#nmersReverse=nmers
					


					i=0
					while(i<lenTarget):
						for nmer in nmers:
							lnmer=len(nmer)
							if elementSeq[i:i+lnmer]==nmer: #match
								ThisPos.append([i,nmer])
								if noOverlap:
									i+=lnmer-1
									break
							
						i+=1
					
						
				

					#
					#
					#try:
					#	while(True):
					#		index=elementSeq.index(Word,cur);
					#		cur=index+1;
					#		ThisPos.append(index);
					#except ValueError:
					#	pass;
				
					
					freq=len(ThisPos)
					if(freq>0):
						#add to the record!
						thisRecord.append([eventIDOutput,lenTarget,freq,ThisPos]);
				
				
	fin.close();

	for header in Occurences.keys():
		PerHeader=Occurences[header];
		for elementKey in PerHeader.keys():
			PerElement=PerHeader[elementKey];
			for familyName,perFamPerElement in PerElement.items():
				#print >> stdout,"Header\tElement\t"+("\t".join(eventIDHeader))+"\tFamily\tFreq\tWord\tLenTarget\tPos"
				for eventIDOutput,lenTarget,freq,ThisPos in perFamPerElement:
					for startInSeq,word in ThisPos:
						print >> stdout, header+"\t"+elementKey+"\t"+("\t".join(eventIDOutput))+"\t"+familyName+"\t"+str(freq)+"\t"+word+"\t"+str(lenTarget)+"\t"+str(startInSeq)			
					




def loadFamilyList(filename,NmerOnly):
	NmerList=dict()
	NmerAlign=dict()
	fil=open(filename)
	curName=""
	for lin in fil:
		lin=lin.rstrip()
		fields=lin.split()
		
		famtest=fields[0].split("_")[0]
		kmer=fields[1]
		
		if famtest!=curName:
			curName=famtest
			if NmerList.has_key(curName):
				print >> stderr,"duplicate family name",curName
				exit()
			curList=[]
			curAlign=[]
			NmerList[curName]=curList
			NmerAlign[curName]=curAlign
		
		kmerNoGap=kmer.replace("-","")
		if NmerOnly!=0 and len(kmerNoGap)!=NmerOnly:
			continue
			
		curAlign.append(kmer)
		curList.append(kmerNoGap) #remove all 
	
	
	fil.close()
	
	for family in NmerList.keys():
		if len(NmerList[family])==0:
			del NmerList[family]
			del NmerAlign[family]
		else:
			NmerList[family].sort(stringLengthDescending)
	
	
	return [NmerList,NmerAlign]

def stringLengthDescending(x,y):
	lx=len(x)
	ly=len(y)
	if lx>ly:
		return -1
	elif lx==ly:
		return 0
	else:
		return 1




def printUsageAndExit(programName):
	#print >> stderr,argv[0]," -1m filename,headerRow1,startRow1,strandCol1,fromCol1,toCol1,N,CGBinInterval,FDRCutOff,pvalueCutOff,topCount";
	#print >> stderr,argv[0]," -pos filename,headerRow1,startRow1,chrCol1,eventIDCol1,geneCol1,coordCol1,fromCol1,toCol1,WordU";	
	#print >> stderr,argv[0]," -h filenamefg,filenamebg,headerRow1,startRow1,strandCol1,fromCol1,toCol1,N,CGBinInterval,FDRCutOff,pvalueCutOff,topCount";
	print >> stderr,programName,"[Options] Algorithm <Algorithm-args>"
	print >> stderr,"input Sequence tables are provided with a header, e.g., inFXse "
	print >> stderr,"Then each row in the column has first 2 chars as the element type, each separated by |, e.g., I3ACAGAC|"
	print >> stderr,"Enrichment results will be given per header per elementtype, e.g., inFXseq/I3"
	print >> stderr,"Two kinds of enrichment can be used"
	print >> stderr,"Hypergeometric (-h) will be used to find motif enriched by hypergeometric word enrichment over background"
	print >> stderr,"1st order markov model (-1mm) will be used to find motif enriched over a 1st order markov model learned from mononucleotide and dinucleotide composition"
	print >> stderr,"Unbiased approach to identify all k-mers are available. Alternatively a targeted approach for identifying a motif family is provided (given the motif sequences or a  gapped alignment of the motif k-mers)"
	print >> stderr,"A tool is also available for finding position of motifs."
	print >> stderr,"Programs:"
	print >> stderr,"1st Markov Model\t1m filename eventIDCols fromCol toCol N-mer CGBinSize"
	print >> stderr,"Hypergeometric\th filenameFG filenameBG fromCol toCol N-mer CGBinInterval" 
	print >> stderr,"Position of Motifs\t-family fam[,nmer] [--no-overlap] pos filename eventIDCols fromCol1 toCol1"
	print >> stderr,"Options:"
	print >> stderr,"--headerRow r [1]"
	print >> stderr,"--startRow r [2]"
	print >> stderr,"--field-separator s: not implemented yet use tab"
	print >> stderr,"--FDR-cutoff (1m,h) f [-1.1]"
	print >> stderr,"--pvalue-cutoff (1m,h) p [-1.1]"
	print >> stderr,"--topCount (1m,h) c [10000000]"
	print >> stderr,"--no-overlap: filter out overlapping motifs (Not implemented yet)"
	print >> stderr,"--family fam[,nmer]: use the [nmer only of] family file (gapped alignment or just list of sequences) instead"
	explainColumns(stderr)
	exit();	
	


#print enrich_pvalue(15519533 , 1613 , 34757 , 5);
#print pvalue_enrichment(15519533 , 1613 , 34757 , 5);
#print enrichment_pvalue(15519533 , 1613 , 34757 , 5);
#exit();

#findMotifFrequencyInSequences(seqs,nmers,noOverlap)

def gapped2Ungapped(aligns):
	L=[]
	for align in aligns:
		L.append(align.replace("-",""))

	return L

#side-effect: NmerAlign is going to change.
def findEnrichmentOfMotifFamilyByShuffling(filename,headerRow1,startRow1,eventIDCols0,fromCol1,toCol1,NmerAlign,noOverlap,nShuffles):
	SequenceHash=dict()
	Results=dict()

	#Results[header][element][fam]	
	
	
	getSimpleSequenceHash(SequenceHash,filename,headerRow1,startRow1,fromCol1,toCol1)

	for familyName,aligns in NmerAlign.items():
		shuffles=[]
		
		oriNmerList=gapped2Ungapped(aligns)

		for i in range(0,nShuffles):
			randomizeAlignMatrix(aligns)
			shuffles.append(gapped2Ungapped(aligns))
		
		
		for header, perelement in SequenceHash.items():
			for element, seqs in perelement:
				print >> stderr,"processing",familyName,header,element
				nBGHigher=0				
				oriFreq=findMotifFrequencyInSequences(seqs,oriNmerList,noOverlap)
				print >> stderr,"origFreq=",oriFreq,"shuffleFreq="			
				for shuffle in shuffles:
					shuffleFreq=findMotifFrequencyInSequences(seqs,shuffle,noOverlap)
					print >> stderr," ",shuffleFreq," "					
					if shuffleFreq>=oriFreq:
						nBGHigher+=1
				
				
				pvalue=float(nBGHigher)/nShuffles
				print >> stderr,"nShuffles=",nShuffles,"nBGHigher=",nBGHigher,"pvalue=",pvalue

				try:
					resultPerHeader=Results[header]
				except KeyError:
					resultPerHeader=dict()
					Results[header]=resultPerHeader

				try:
					resultPerElement=resultPerHeader[element]
				except KeyError:
					resultPerElement=dict()
					resultPerHeader[element]=resultPerElement

				resultPerElement[familyName]=[pvalue,oriFreq,nBGHigher]
					
	#now need something that calculate FDR and sort the p-value and output results.

	#####here!!

	

if __name__=="__main__":
	headerRow=1
	startRow=2
	separator="\t"
	FDRCutOff=-1.1
	pvalueCutOff=-1.1
	topCount=10000000
	noOverlap=False
	familyFileName=""
	NmerList=dict()
	NmerAlign=dict()

	programName=argv[0]
	opts,args=getopt(argv[1:],'',["headerRow=","startRow=","field-separator=","FDR-cutoff=","pvalue-cutoff=","topCount=","no-overlap","family="])

	#try:
	for a,v in opts:
		if a=='--headerRow':
			headerRow=int(v)
		elif a=='--startRow':
			startRow=int(v)
		elif a=='--field-separator':
			separator=v
		elif a=='--FDR-cutoff':
			FDRCutOff=float(v)
		elif a=='--pvalue-cutoff':
			pvalueCutOff=float(v)
		elif a=='--topCount':
			topCount=int(v)	
		elif a=='--no-overlap':
			noOverlap=True
		elif a=='--family':
			familyFileName=v.split(",")
			if len(familyFileName)==2:
				NmerOnly=int(familyFileName[1])
			else:
				NmerOnly=0
			NmerList,NmerAlign=loadFamilyList(familyFileName[0],NmerOnly)
			print >> stderr,NmerList
		
		
	if len(args)<2:
		printUsageAndExit(programName);
		
	fileName=args[1]
	header,prestarts=getHeader(fileName,headerRow,startRow,separator)

	program=args[0]
	if(program=="1m"):
		print >> sys.stderr, "args[]:",args;
		filename, idCol1, fromCol1, toCol1, Nmer, CGBinSize=args[1:]
		fromCol1=getCol0ListFromCol1ListStringAdv(header,fromCol1)
		toCol1=getCol0ListFromCol1ListStringAdv(header,toCol1)	
		idCol0=getCol0ListFromCol1ListStringAdv(header,idCol1)
		Nmer=int(Nmer)
		CGBinSize=int(CGBinSize)
			
		#findEnrichedMotifBy1MM(filename,headerRow1,startRow1,fromCol1,toCol1,N,CGBinSize,FDRCutOff,pvalueCutOff,topCount)
		findEnrichedMotifBy1MM(filename,headerRow,startRow,min(fromCol1)+1,max(toCol1)+1,Nmer,CGBinSize,FDRCutOff,pvalueCutOff,topCount,NmerList,noOverlap,idCol0);
	#elif(program=="h"):
	#	print >> sys.stderr, "args[]:",args;
	#	filenameFG,filenameBG,fromCol1,toCol1,Nmer,CGBinInterval=args[1:]
	#	fromCol1=getCol0ListFromCol1ListStringAdv(header,fromCol1)
	#	toCol1=getCol0ListFromCol1ListStringAdv(header,toCol1)		
	#	CGBinInterval=float(CGBinInterval)
	#	Nmer=int(Nmer)
	#	#findEnrichedMotifByHGWE(filenamefg,filenamebg,headerRow1,startRow1,fromCol1,toCol1,N,CGBinInterval,FDRCutOff,pvalueCutOff,topCount)
	#	findEnrichedMotifByHGWE(filenameFG,filenameBG,headerRow,startRow,min(fromCol1)+1,max(toCol1)+1,Nmer,CGBinInterval,FDRCutOff,pvalueCutOff,topCount,NmerList);
	
	elif(program=="pos"):

		print >> sys.stderr, "args[]:",args;
		filename ,eventIDCols ,fromCol1, toCol1 =args[1:]
		fromCol1=getCol0ListFromCol1ListStringAdv(header,fromCol1)
		toCol1=getCol0ListFromCol1ListStringAdv(header,toCol1)	
		eventIDCols0=getCol0ListFromCol1ListStringAdv(header,eventIDCols)	
	
		findMotifPositions2(filename,headerRow,startRow,eventIDCols0,min(fromCol1)+1,max(toCol1)+1,NmerList,noOverlap);
	
		#findMotifPositions(filename,headerRow1,startRow1,chrCol1,eventIDCol1,geneCol1,coordCol1,fromCol1,toCol1,WordU):
	#	findMotifPositions(argv[2],int(argv[3]),int(argv[4]),int(argv[5]),int(argv[6]),int(argv[7]),int(argv[8]),int(argv[9]),int(argv[10]),argv[11]);
	else:
		print >> stderr,"Unknown subroutine:",program
		printUsageAndExit(programName)
		

	#except:
		#printUsageAndExit(programName);

