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

import warnings
warnings.simplefilter('ignore', DeprecationWarning)

#import hypergeom
#from hypergeom import pvalue_enrichment
from getopt import getopt
import shelve
import sys
from sys import *
from math import log
from random import shuffle
from pvalue_module import *

from albertcommon import *

termSeperator="|"

from JHypergeometricPvalue import JHypergeometricPvalue

ErrorBinRealValue=-10000000.00


def getBinKey(binV,binDivider):
	global ErrorBinRealValue
	if binV==ErrorBinRealValue:
		return 0

	return int(binV/binDivider)+1

#binDivider=-1 to indicates calculate binDivider! onlyTerms=[] use all terms; minTermMemberCount==0 => no filtering on termMemberCount
def calTerms(TERMS,filename,GeneIDCol,TermCol,BinCol,startRow1,allowDuplicate,numBins,binDivider,logBinValue,onlyTheseTerms,minTermMemberCount,maxTermMemberCount,minTermFraction,maxTermFraction):
	global termSeperator,ErrorBinRealValue
	
	genes=set()
	
	nTerms=0
	nGenes=0	
	geneBins=dict()
	
	geneExp=[]
	maxExp=-100000.00
	minExp=100000.00


	fil=open(filename)
	ReqCol=max(GeneIDCol,TermCol,BinCol)
	lino=0
	for lin in fil:
		lino+=1
		if(lino<startRow1):
			continue
		lin=lin.rstrip("\r\n")
		spliton=lin.split("\t")
		if(len(spliton)<ReqCol+1):
			#print >> stderr,"Invalid Col numbers, ignored:",lin
			continue
		
		valueToBin=float(spliton[BinCol])
		if logBinValue:
			if valueToBin==0.0:
				valueToBin=ErrorBinRealValue
			else:
				valueToBin=log(valueToBin)

		
				
		incNGenes=False


		ThisID=spliton[GeneIDCol]
		ThisEntryTerms=spliton[TermCol].split(termSeperator)

		geneExp.append((valueToBin,ThisID))

		if valueToBin!=ErrorBinRealValue:
			maxExp=max(valueToBin,maxExp)
			minExp=min(valueToBin,minExp)


		for term in ThisEntryTerms:
			term=term.strip()
			if(len(term)<1):
				continue

			if len(onlyTheseTerms)>0 and term not in onlyTheseTerms:
				continue
			
			if not TERMS.has_key(term):
				nTerms+=1				
				TERMS[term]=[]



			if allowDuplicate:
				
				TERMS[term].append(ThisID)
				incNGenes=True

				
			else:
				if not incNGenes and ThisID not in genes:
					incNGenes=True
					genes.add(ThisID)


				if ThisID not in TERMS[term]:
					incNGenes=True
					TERMS[term].append(ThisID)

		if incNGenes:
			nGenes+=1
			
	#do we need to calculate binDivider?
	if binDivider==-1: #yes
		binDivider=(maxExp-minExp)/numBins
	
	#now go to each geneExp and hash
	for valueToBin,ThisID in geneExp:
		binKey=getBinKey(valueToBin,binDivider)
		try:
			binContent=geneBins[binKey]
		except KeyError:
			binContent=[]
			geneBins[binKey]=binContent

		if allowDuplicate or ThisID not in binContent:
			binContent.append(ThisID)

	
	
	#now filter terms
	for term,termContent in TERMS.items():
		if "__$$$" in term:
			continue

		nGenesInTerm=len(termContent)
		fGenesInTerm=float(nGenesInTerm)/nGenes
		if nGenesInTerm<minTermMemberCount or nGenesInTerm>maxTermMemberCount or fGenesInTerm<minTermFraction or fGenesInTerm>maxTermFraction:
			nTerms-=1
			del TERMS[term]
	
	TERMS["__$$$NGENES"]=nGenes
	TERMS["__$$$NTERMS"]=nTerms
	TERMS["__$$$GENEBINS"]=geneBins

	return binDivider

def drawMatchedItems(BgGeneBins,FgGeneBins):
	DrawnList=[]

	for binKey,FgBinContent in FgGeneBins.items():
		
		BgBinContent=BgGeneBins[binKey]
		numItemsInFgBin=len(FgBinContent)
		numItemsInBgBin=len(BgBinContent)

		if numItemsInBgBin<numItemsInFgBin:
			print >> stderr,"warning: Bg bin has fewer items than fg bins: unable to perform permutation on this bin:","binkey="+str(binKey),"fg#="+str(numItemsInFgBin),"bg#="+str(numItemsInBgBin)
			#continue
			#exit()			

		if numItemsInBgBin==0:
			continue

		shuffle(BgBinContent)		
		DrawnList.extend(BgBinContent[:min(numItemsInBgBin,numItemsInFgBin)])

	return DrawnList


def intersectLists(L1,L2):
	return list( set(L1) & set(L2) )

def subsetOf(BigSet,SmallSet,allowDuplicate):
	subSet=[]

	if allowDuplicate:
		for b in BigSet:
			if b in SmallSet:
				subSet.append(b)

		return subSet
	else:
		return intersectLists(BigSet,SmallSet)


def enrich(FGTerms,nGenesFG,FGData,nGenesBG,BGData,geneIDConstraints,allowDuplicates,ignoreWorseThanBackgroundTerms,minSamt,HGWEPvalueCutOff): #=> returns [[samt,sam,popt,pop,FGTermEntry,term]],[pvalue],[FDR] geneIDConstraints=[] => no constraints

	constraint=(len(geneIDConstraints)>0)	

	JavaInputMatrix=[]	

	for term in FGTerms:
		if "__$$$" in term:
			continue

		if not BGData.has_key(term):
			print >> stderr, "Error: term",term,"not found in background"
			sys.exit()
		
		BGTermEntry=BGData[term]
		FGTermEntry=FGData[term]

		pop=nGenesBG
		popt=len(BGTermEntry)

		sam=nGenesFG

		if constraint:
			#now overlap
			FGTermEntryToInclude=subsetOf(FGTermEntry,geneIDConstraints,allowDuplicates)
		else:
			FGTermEntryToInclude=FGTermEntry

		samt=len(FGTermEntryToInclude)
		JavaInputMatrix.append([samt,sam,popt,pop,FGTermEntryToInclude,term])

	
	if len(JavaInputMatrix)==0:
		print >> stderr,"JavaInputMatrix Empty"
		sys.exit()

	JavaPvalues=JHypergeometricPvalue(JavaInputMatrix,-1)
	
	if ignoreWorseThanBackgroundTerms:
		for i in range(0,len(JavaInputMatrix)):
			samt,sam,popt,pop,FGTermEntryToInclude,term=JavaInputMatrix[i]
			if float(samt)/sam<=float(popt)/pop:
				JavaPvalues[i]=2.0
			elif samt<minSamt:
				JavaPvalues[i]=2.0
			elif JavaPvalues[i]>HGWEPvalueCutOff:
				JavaPvalues[i]=2.0


	if len(JavaPvalues)==0:
		print >> stderr,"JPvalue error"
		sys.exit()

	FDR=getFDRfromPvalue(JavaPvalues)

	return (JavaInputMatrix,JavaPvalues,FDR)
		


	






def main(BgShelve, BgFile, BgGeneIDCol, BgTermCol, BgBinCol, BgStartRow1, FgFile, FgGeneIDCol, FgTermCol, FgBinCol, FgStartRow1,recomputeBg,useJava,allowDuplicate,numBins,logBinValues,ndraws,minPopt,ignoreWorseThanBackgroundTerms,minSamt,HGWEPvalueCutOff,useTerms,maxPopt,minfe,minSamf,minPopf,maxPopf,excludeFGGenesFromRandomSets):
	global termSeperator
	
	
	if not recomputeBg:
		saved=shelve.open(BgShelve)
		
		if not saved.has_key("BG"):
			recomputeBg=True		
		else:
			BGData=saved["BG"]
			if len(BGData)<1 or not BGData.has_key("__$$$NGENES"):
				recomputeBg=True

			if not BGData.has_key("__$$$NUMBINS") or BGData["__$$$NUMBINS"]!=numBins:
				recomputeBg=True

			if not BGData.has_key("__$$$MINPOPT") or BGData["__$$$MINPOPT"]!=minPopt:
				recomputeBg=True

			if not BGData.has_key("__$$$MAXPOPT") or BGData["__$$$MAXPOPT"]!=maxPopt:
				recomputeBg=True

			if not BGData.has_key("__$$$MINPOPF") or BGData["__$$$MINPOPF"]!=minPopf:
				recomputeBg=True

			if not BGData.has_key("__$$$MAXPOPF") or BGData["__$$$MAXPOPF"]!=maxPopf:
				recomputeBg=True

			#if not BGData.has_key("__$$$TERMUNIVERSE") or BGData["__$$$TERMUNIVERSE"]!=useTerms
			#	recomputeBg=True
		saved.close()

	if recomputeBg:
		print >> stderr, "recal BG"
		BGData=dict()#=shelve.open(BgShelve)

		#TERMS,filename,GeneIDCol,TermCol,BinCol,startRow1,allowDuplicate,numBins,binDivider,logBinValue
		binDivider=calTerms(BGData,BgFile,BgGeneIDCol,BgTermCol,BgBinCol,BgStartRow1,allowDuplicate,numBins,-1,logBinValues,useTerms,minPopt,maxPopt,minPopf,maxPopf)
		BGData["__$$$BINDIVIDER"]=binDivider
		BGData["__$$$NUMBINS"]=numBins
		BGData["__$$$MINPOPT"]=minPopt
		BGData["__$$$MAXPOPT"]=maxPopt
		BGData["__$$$MINPOPF"]=minPopf
		BGData["__$$$MAXPOPF"]=maxPopf
		saved=shelve.open(BgShelve)
		saved["BG"]=BGData
		saved.close()
	else:
		binDivider=BGData["__$$$BINDIVIDER"]

	print >> stderr,"bindivider=",binDivider
	
	

	
	FGData=dict()
	
	#if minPopt==0:
	#	OnlyTheseTerms=useTerms ###why????!
	#else:
	OnlyTheseTerms=BGData.keys() ####

	#TERMS,filename,GeneIDCol,TermCol,BinCol,startRow1,allowDuplicate,numBins,binDivider,logBinValue
	#calTerms(FGData,FgFile,FgGeneIDCol,FgTermCol,FgBinCol,FgStartRow1,allowDuplicate,0,binDivider,logBinValues,OnlyTheseTerms,0,1000000000,-100,1000000000) ##not filtering anything
	calTerms(FGData,FgFile,FgGeneIDCol,FgTermCol,FgBinCol,FgStartRow1,allowDuplicate,0,binDivider,logBinValues,OnlyTheseTerms,minSamt,1000000000,minSamf,1000000000) ##not filtering anything
	#directly incorporate minSamt,minSamf into this

	#now calculate GO enrichment and FDR

	

	nTermsBG=BGData["__$$$NTERMS"]
	nGenesBG=BGData["__$$$NGENES"]
	BGBins=BGData["__$$$GENEBINS"]

	nTermsFG=FGData["__$$$NTERMS"]
	nGenesFG=FGData["__$$$NGENES"]
	FGBins=FGData["__$$$GENEBINS"]
	print >> stderr,"FGBins=",FGBins


	if excludeFGGenesFromRandomSets:
		#make a new BGBins which doesn't have FG genes
		FGGeneSet=set()		
		for fgGeneVectors in FGBins.values():
			for g in fgGeneVectors:
				FGGeneSet.add(g)

		newBGBins=dict()
		if allowDuplicate:
			for oldKey,oldGenes in BGBins.items():
				newGenes=[]
				newBGBins[oldKey]=newGenes
				for g in oldGenes:
					if g not in FGGeneSet:
						newGenes.append(g)								
		else:
			for oldKey,oldGenes in BGBins.items():
				newGenes=[]
				newBGBins[oldKey]=list(set(oldGenes)-FGGeneSet)

		#now replace
		BGBins=newBGBins	
						

	randomGeneLists=drawMatchedItems(BGBins,FGBins)

	FGTerms=FGData.keys()

	print >> stderr,"calculate main"
	MainFractionInfo,MainPvalues,MainFDRs=enrich(FGTerms,nGenesFG,FGData,nGenesBG,BGData,[],allowDuplicate,ignoreWorseThanBackgroundTerms,minSamt,HGWEPvalueCutOff) #the main one

	#for per term:	
	numRandomFractionExtreme=[]
	numRandompvExtreme=[] 

	#init:
	for i in range(0,len(FGTerms)):
		numRandomFractionExtreme.append(0)
		numRandompvExtreme.append(0)

	for draw_i in range(0,ndraws):
		print >> stderr,"drawing ",(draw_i+1),"of",ndraws
		drawn_list=drawMatchedItems(BGBins,FGBins)
		ThisDrawFractionInfo,ThisDrawPvalues,ThisDrawFDRs=enrich(FGTerms,nGenesFG,BGData,nGenesBG,BGData,drawn_list,allowDuplicate,False,0,2.0) #do not ignore worse than background terms for random sets, no samt cutoff, no pvaluecutoff
		
		#now goto each term in main and this draw
		for itemIdx,main_fraction_info,main_pvalue,main_fdr,thisdraw_fraction_info,thisdraw_pvalue,thisdraw_fdr in zip(range(0,len(FGTerms)),MainFractionInfo,MainPvalues,MainFDRs,ThisDrawFractionInfo,ThisDrawPvalues,ThisDrawFDRs):
			main_samt,main_sam,main_popt,main_pop,main_ids,main_term=main_fraction_info
			thisdraw_samt,thisdraw_sam,thisdraw_popt,thisdraw_pop,thisdraw_ids,thisdraw_term=thisdraw_fraction_info
			
			if main_term!=thisdraw_term:
				print >> stderr,"bug! main_term!=thisdraw_term"
				exit()
				

			main_samf=float(main_samt)/main_sam
			thisdraw_samf=float(thisdraw_samt)/thisdraw_sam

			if thisdraw_samf>=main_samf:
				numRandomFractionExtreme[itemIdx]+=1
			
			if thisdraw_pvalue<=main_pvalue:
				numRandompvExtreme[itemIdx]+=1



	pvalueRandomFraction=[]
	pvalueRandompv=[]
		
	for num_random_fraction_extreme,num_random_pv_extreme,main_pvalue in zip(numRandomFractionExtreme,numRandompvExtreme,MainPvalues):
		if main_pvalue==2.0:
			pvalueRandomFraction.append(2.0)
			pvalueRandompv.append(2.0)
		else:
			pvalueRandomFraction.append(float(num_random_fraction_extreme)/ndraws)
			pvalueRandompv.append(float(num_random_pv_extreme)/ndraws)

	FDRRandomFraction=getFDRfromPvalue(pvalueRandomFraction)
	FDRRandompv=getFDRfromPvalue(pvalueRandompv)

	#now output!
	fieldsToOutput=[]

	
	
	fieldsToOutput.append("term")
	fieldsToOutput.append("popt")
	fieldsToOutput.append("pop")
	fieldsToOutput.append("popt/pop")
	fieldsToOutput.append("samt")
	fieldsToOutput.append("sam")
	fieldsToOutput.append("samt/sam")
	fieldsToOutput.append("foldEnrichment")
	fieldsToOutput.append("genes")
	fieldsToOutput.append("HGWE.pvalue")
	fieldsToOutput.append("HGWE.FDR")
	fieldsToOutput.append("RF.pvalue")			
	fieldsToOutput.append("RF.FDR")
	fieldsToOutput.append("Rpv.pvalue")
	fieldsToOutput.append("Rpv.FDR")
	print >> stdout,"\t".join(fieldsToOutput)

	for main_fraction_info,main_pvalue,main_fdr,rf_pvalue,rf_fdr,rpv_pvalue,rpv_fdr in zip(MainFractionInfo,MainPvalues,MainFDRs,pvalueRandomFraction,FDRRandomFraction,pvalueRandompv,FDRRandompv):
		main_samt,main_sam,main_popt,main_pop,main_ids,main_term=main_fraction_info
		main_samf=float(main_samt)/main_sam
		main_popf=float(main_popt)/main_pop
		fEnrichment=main_samf/main_popf
		fieldsToOutput=[main_term,main_popt,main_pop,main_popf,main_samt,main_sam,main_samf,fEnrichment,"|".join(main_ids),main_pvalue,main_fdr,rf_pvalue,rf_fdr,rpv_pvalue,rpv_fdr]
		toStrArrayInPlace(fieldsToOutput)
		print >> stdout,"\t".join(fieldsToOutput)

def printUsageAndExit(programName):
	print >> stderr, "Usage:",programName,"BgShelve BgFile BgGeneIDCol BgTermCol BgBinCol BgStartRow FgFile FgGeneIDCol FgTermCol FgBinCol FgStartRow"
	print >> stderr, "Option"
	print >> stderr, "--term-sep=|"
	print >> stderr, "--force-recompute-bg"
	print >> stderr, "[--no-duplicate], --allow-duplicate"
	print >> stderr, "--num-bins=10"
	print >> stderr, "--log-bin-values=False"
	print >> stderr, "--ndraws=1000"
	print >> stderr, "--min-popt=5 minimum number of genes annotated in the background to that term"
	print >> stderr, "--ignore-worse-than-background-terms set p-value of those terms to 2.0"
	print >> stderr, "--HGWE-pvalue-cutoff=2.0 (no cutoff)"
	print >> stderr, "--min-samt=2 minimum number of genes annotated in the foreground to that term"
	print >> stderr, "--select-terms-in filename use only terms specified in files, can do this multiple times"
	explainColumns(stderr)	
	#print >> stderr, 
	
	
	exit()

def toStrArrayInPlace(L):
	for i in range(0,len(L)):
		L[i]=str(L[i])

if __name__=='__main__':
	
	programName=argv[0]
	opts, argvs = getopt(argv[1:],'',["term-sep=","force-recompute-bg","use-java","use-c","no-duplicate","allow-duplicate","num-bins=","log-bin-values","ndraws=","min-popt=","ignore-worse-than-background-terms","HGWE-pvalue-cutoff=","min-samt=",'max-popt=','min-samf=','min-popf=','max-popf=','select-terms-in=','min-fe=','exclude-fg-from-random-sets'])

	recomputeBg=False
	fs="\t"
	allowDuplicate=False
	useJava=True
	numBins=50
	logBinValues=False
	nDraws=1000
	minPopt=5
	maxPopt=10000000
	minPopf=-1.0
	maxPopf=2.0
	minSamf=-1.0
	minfe=-1.0
	excludeFGGenesFromRandomSets=False
	ignoreWorseThanBackgroundTerms=False
	HGWEPvalueCutOff=2.0
	minSamt=2
	useTermsIn=[]
	for o,a in opts:
		if o=="--force-recompute-bg":
			recomputeBg=True
		elif o=="--term-sep":
			termSeperator=a
		elif o=="--use-java":
			useJava=True
		elif o=="--use-c":
			useJava=False
		elif o=="--allow-duplicate":
			allowDuplicate=True
		elif o=="--no-duplicate":
			allowDuplicate=False
		elif o=="--num-bins":
			numBins=int(a)
		elif o=="--log-bin-values":
			logBinValues=True
		elif o=="--ndraws":
			nDraws=int(a)
		elif o=='--min-popt':
			minPopt=int(a)
		elif o=='--max-popt':
			maxPopt=int(a)
		elif o=="--min-samt":
			minSamt=int(a)
		elif o=='--min-samf':
			minSamf=float(a)
		elif o=='--min-popf':
			minPopf=float(a)
		elif o=='--max-popf':
			maxPopf=float(a)
		elif o=='--min-fe':
			minfe=float(a)
		elif o=='--exclude-fg-from-random-sets':
			excludeFGGenesFromRandomSets=True
		elif o=="--ignore-worse-than-background-terms":
			ignoreWorseThanBackgroundTerms=True
		elif o=="--HGWE-pvalue-cutoff":
			HGWEPvalueCutOff=float(a)
		elif o=='--select-terms-in':
			useTermsIn.append(a)
	try:
		BgShelve, BgFile, BgGeneIDCol, BgTermCol, BgBinCol, BgStartRow, FgFile, FgGeneIDCol, FgTermCol, FgBinCol, FgStartRow = argvs
	except:
		printUsageAndExit(programName)


	BgStartRow=int(BgStartRow)
	FgStartRow=int(FgStartRow)

	#for bg file:
	headerBG,prestartsBG=getHeader(BgFile,BgStartRow-1,BgStartRow,fs)
	BgGeneIDCol=getCol0ListFromCol1ListStringAdv(headerBG,BgGeneIDCol)[0]
	BgTermCol=getCol0ListFromCol1ListStringAdv(headerBG,BgTermCol)[0]
	BgBinCol=getCol0ListFromCol1ListStringAdv(headerBG,BgBinCol)[0]	

	#for fg file
	headerFG,prestartsFG=getHeader(FgFile,FgStartRow-1,FgStartRow,fs)
	FgGeneIDCol=getCol0ListFromCol1ListStringAdv(headerFG,FgGeneIDCol)[0]	
	FgTermCol=getCol0ListFromCol1ListStringAdv(headerFG,FgTermCol)[0]	
	FgBinCol=getCol0ListFromCol1ListStringAdv(headerFG,FgBinCol)[0]	
	
	useTerms=[]

	if len(useTermsIn)>0:
		for utfilename in useTermsIn:
			utfile=open(utfilename)
			#lines=utfile.readlines()
			for lin in utfile:
				useTerms.append(lin.strip().split("\t")[0])
			utfile.close()		
			

	
#main(BgShelve, BgFile, BgGeneIDCol, BgTermCol, BgBinCol, BgStartRow1, FgFile, FgGeneIDCol, FgTermCol, FgBinCol, FgStartRow1,recomputeBg,useJava,allowDuplicate,numBins,logBinValues,ndraws)

	main(BgShelve,BgFile,BgGeneIDCol,BgTermCol,BgBinCol,BgStartRow,FgFile,FgGeneIDCol,FgTermCol,FgBinCol,FgStartRow,recomputeBg,useJava,allowDuplicate,numBins,logBinValues,nDraws,minPopt,ignoreWorseThanBackgroundTerms,minSamt,HGWEPvalueCutOff,useTerms,maxPopt,minfe,minSamf,minPopf,maxPopf,excludeFGGenesFromRandomSets)

