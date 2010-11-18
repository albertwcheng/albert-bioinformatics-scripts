#!/usr/bin/env python

'''

Convert PSL format from BLAT output to BED format.

PSL format specification:
http://genome.ucsc.edu/goldenPath/help/blatSpec.html
http://genome.ucsc.edu/FAQ/FAQformat#format2

BED format specification:
http://genome.ucsc.edu/FAQ/FAQformat#format1

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
from optparse import OptionParser
from sys import *


PSL_matchesI=0
PSL_misMatchesI=1
PSL_repMatchesI=2
PSL_QSizeI=10

BED_blockSizesI=10
BED_blockStartsI=11

def strArrayToIntArrayInPlace(L):
	for i in range(0,len(L)):
		L[i]=int(L[i])
		
def toStrArray(L):
	S=[]
	for x in L:
		S.append(str(x))
	
	return S

def parsePSLLine(fields):
	try:
		#allocate the fields into the different var	
		matches,misMatches,repMatches,nCount,qNumInsert,qBaseInsert,tNumInsert,tBaseInsert,strand,qName,qSize,qStart,qEnd,tName,tSize,tStart,tEnd,blockCount,blockSizes,qStarts,tStarts=fields
	
		#now recast the vars
		matches=int(matches)
		misMatches=int(misMatches)
		repMatches=int(repMatches)
		nCount=int(nCount)
		qNumInsert=int(qNumInsert)
		qBaseInsert=int(qBaseInsert)
		tNumInsert=int(tNumInsert)
		tBaseInsert=int(tBaseInsert)
		qSize=int(qSize)
		qStart=int(qStart)
		qEnd=int(qEnd)
		tSize=int(tSize)
		tStart=int(tStart)
		tEnd=int(tEnd)
		blockCount=int(blockCount)
		blockSizes=blockSizes.split(",")[0:blockCount] #avoid the last empty split due to the last comma
		qStarts=qStarts.split(",")[0:blockCount] 
		tStarts=tStarts.split(",")[0:blockCount] 		
		strArrayToIntArrayInPlace(blockSizes)
		strArrayToIntArrayInPlace(qStarts)
		strArrayToIntArrayInPlace(tStarts)
		return (qName,[matches,misMatches,repMatches,nCount,qNumInsert,qBaseInsert,tNumInsert,tBaseInsert,strand,qName,qSize,qStart,qEnd,tName,tSize,tStart,tEnd,blockCount,blockSizes,qStarts,tStarts]) #return back the converted fields
	except:
		return ("",[]) #return empty list if failed
		
		
def PSLFields2BedFields(PSLfields,itemRgb,score):
	matches,misMatches,repMatches,nCount,qNumInsert,qBaseInsert,tNumInsert,tBaseInsert,strand,qName,qSize,qStart,qEnd,tName,tSize,tStart,tEnd,blockCount,blockSizes,qStarts,tStarts=PSLfields
	chrom=tName
	chromStart=tStart
	chromEnd=tEnd
	name=qName
	#score
	#strand
	thickStart=tStart
	thickEnd=tEnd
	#itemRgb
	#blockCount
	#blockSizes
	blockStarts=[]
	for tStar in tStarts:
		blockStarts.append(tStar-chromStart)
		
	return [chrom,chromStart,chromEnd,name,score,strand,thickStart,thickEnd,itemRgb,blockCount,blockSizes,blockStarts]
	
	
def outputBedEntry(stream,BEDfields):
	toOut=BEDfields[:]
	toOut[BED_blockSizesI]=",".join(toStrArray(toOut[BED_blockSizesI]))
	toOut[BED_blockStartsI]=",".join(toStrArray(toOut[BED_blockStartsI]))
	print >> stream,"\t".join(toStrArray(toOut))


#selector will receive the fields of the entry, and return those with best (can be multiple) as a list
#which will be further passed to downstream selectors
def biggestNumMatchSelector(PSLEntries):
	EntryNames=PSLEntries.keys()
	
	for PSLEntryQName in EntryNames:
		coQNameEntries=PSLEntries[PSLEntryQName]
		
		maxNumMatches=-1
 		indxWithMax=[]
 		for i in range(len(coQNameEntries)-1,-1,-1):
 			thisEntry=coQNameEntries[i]
			thisMatches=thisEntry[PSL_matchesI]
			thisRepMatches=thisEntry[PSL_repMatchesI]
			thisTotalMatches=thisMatches+thisRepMatches
			if thisTotalMatches>maxNumMatches:
				maxNumMatches=thisTotalMatches
				indxWithMax=[i]			
			elif thisTotalMatches==maxNumMatches:
				indxWithMax.append(i)
				
		newCoQ=[]
		PSLEntries[PSLEntryQName]=newCoQ
		for indxWanted in indxWithMax:
			newCoQ.append(coQNameEntries[indxWanted])
			
	
def smallestNumRepMatches(PSLEntries):
	EntryNames=PSLEntries.keys()
	
	for PSLEntryQName in EntryNames:
		coQNameEntries=PSLEntries[PSLEntryQName]
		
		minNumRepMatches=10000000
 		indxWithMin=[]
 		for i in range(len(coQNameEntries)-1,-1,-1):
 			thisEntry=coQNameEntries[i]
			thisRepMatches=thisEntry[PSL_repMatchesI]
			if thisRepMatches<minNumRepMatches:
				minNumRepMatches=thisRepMatches
				indxWithMin=[i]			
			elif thisRepMatches==minNumRepMatches:
				indxWithMin.append(i)
		
		newCoQ=[]
		PSLEntries[PSLEntryQName]=newCoQ
		for indxWanted in indxWithMin:
			newCoQ.append(coQNameEntries[indxWanted])		

def reduceToOnePerQName(PSLEntries):
	for PSLEntryQName,coQNameEntries in PSLEntries.items():
		del coQNameEntries[1:]

def filterFractionMatches(PSLEntries,filterFractionMatched):
	for PSLEntryQName,coQNameEntries in PSLEntries.items():
		for i in range(len(coQNameEntries)-1,-1,-1): #from end, for easy deletion
			thisEntry=coQNameEntries[i]
			thisMatches=thisEntry[PSL_matchesI]
			thisRepMatches=thisEntry[PSL_repMatchesI]
			thisQSize=thisEntry[PSL_QSizeI]
			fractionMatched=float(thisMatches+thisRepMatches)/thisQSize
			if fractionMatched<filterFractionMatched:
				del coQNameEntries[i] #not pass this filter, del!	



if __name__=='__main__':
	programName=argv[0]

	bestSelectors=dict()
	bestSelectors["max-num-matches"]=biggestNumMatchSelector
	bestSelectors["min-rep-matches"]=smallestNumRepMatches

	helpSelectBestBy="select the best by an array of selector. Use then-by's to resolve ties. i.e., --select-best-by x --then-by y --then-by z. Available options are "+",".join(bestSelectors.keys())
	parser=OptionParser(usage="Usage: %prog [options] pslfile1 ... > bedfileoutput")
	parser.add_option("--select-best-by",dest="selectFuncs",action="append",help=helpSelectBestBy)
	parser.add_option("--then-by",dest="selectFuncs",action="append",help=helpSelectBestBy)
	parser.add_option("--filter-fraction-matched",dest="filterFractionMatched",default=0,type="float",help="set the min fraction matched from 0.0 to 1.0 [0.0]")
	parser.add_option("--output-only-one-per-query",dest="outputOnlyOnePerQuery",default=False,action="store_true",help="output only (at most) one bed entry per PSL query name")
	parser.add_option("--order-by-qname",dest="orderByQName",default=False,action="store_true",help="output the bed entries sorted by qnames [default: by first apperance]")
	parser.add_option("--itemRgb",dest="itemRgb",default="0,0,0",help="set bed itemRgb [0,0,0]")
	parser.add_option("--score",dest="score",default="0",help="set bed score [0]")
	
	options,args=parser.parse_args()
	
	#now check select funcs validity
	if options.selectFuncs:
		for selecfuncName in options.selectFuncs:
			if selecfuncName not in bestSelectors:
				print >> stderr,"selector function",selecfuncName,"not available. Abort"
				parser.print_help(stderr)
				exit()
	
	#now parse the file!
	try:
		pslfiles=args
		if len(pslfiles)==0:
			raise ValueError
	except:
		parser.print_help(stderr)
		exit()
	
	qNames=[] #ordered list of qNames in order of appearance.
	PSLEntries=dict()
	
	
	for pslfile in pslfiles:
		
		print >> stderr,"loading PSL file",pslfile
		
		lino=0
		
		fil=open(pslfile)
		for lin in fil:
			lino+=1
			fields=lin.rstrip("\r\n").split("\t")
			thisPSLEntryQName,thisPSLEntry=parsePSLLine(fields)
			if len(thisPSLEntry)==0:
				print >> stderr,"\tskip line",lino
				continue
			
			if thisPSLEntryQName not in qNames:
				qNames.append(thisPSLEntryQName)
				coQNameEntries=[]
				PSLEntries[thisPSLEntryQName]=coQNameEntries
			else:
				coQNameEntries=PSLEntries[thisPSLEntryQName]
			
			coQNameEntries.append(thisPSLEntry)
			
			
		fil.close()
		
		
	if options.filterFractionMatched>0:
		#this feature is on
		print >> stderr,"filtering by fraction matched >=",options.filterFractionMatched
		filterFractionMatches(PSLEntries,options.filterFractionMatched)
		
	#now select!~
	if options.selectFuncs:
		print >> stderr,"applying selector",selecfuncName
		for selecfuncName in options.selectFuncs:
			bestSelectors[selecfuncName](PSLEntries)
		
	#now we are almost Done:
	if options.outputOnlyOnePerQuery:
		reduceToOnePerQName(PSLEntries)
	
	if options.orderByQName:
		qNames.sort()
	
	#now output
	for queryName in qNames:
		thisEntries=PSLEntries[queryName]
		for PSLEntry in thisEntries:
			bedEntry=PSLFields2BedFields(PSLEntry,options.itemRgb,options.score)
			outputBedEntry(stdout,bedEntry)