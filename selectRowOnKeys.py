#!/usr/bin/env python

from albertcommon import *
from sys import *
from getopt import getopt
from math import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[rules/options] filename keys"
	print >> stderr,"Rules are applied in order supplied in command"
	print >> stderr,"--minS col: min on string land at col"
	print >> stderr,"--maxS col: max on string land at col"
	print >> stderr,"--minN col: min on number land at col"
	print >> stderr,"--maxN col: max on number land at col"
	exit(1)

def absf(x):
	return fabs(float(x))

def applyMin(col,entries,conv):
	#return back the one satifying the rules
	minEntryI=[0]
	minValue=conv(entries[0][col])
	for i in range(1,len(entries)):
		if conv(entries[i][col])<minValue:
			minValue=conv(entries[i][col])
			minEntryI=[i]
		elif conv(entries[i][col])==minValue:
			minEntryI.append(i)
	return minEntryI,minValue

def applyMax(col,entries,conv):
	maxEntryI=[0]
	maxValue=conv(entries[0][col])
	for i in range(1,len(entries)):
		if conv(entries[i][col])>maxValue:
			maxValue=conv(entries[i][col])
			maxEntryI=[i]
		elif conv(entries[i][col])==maxValue:
			maxEntryI.append(i)
		
		
	return maxEntryI,maxValue	
	
	

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['maxS=','minS=','minN=','maxN=','minAbs=','maxAbs='])
	
	
	rules=[]
	headerRow=1
	startRow=2
	fs="\t"
	try:
		filename,keys=args
	except:
		printUsageAndExit(programName)
		
	
	for o,v in opts:
		if o=='--maxS':
			rules.append([applyMax,str,v])
		elif o=='--minS':
			rules.append([applyMin,str,v])
		elif o=='--maxN':
			rules.append([applyMax,float,v])
		elif o=='--minN':
			rules.append([applyMin,float,v])
		elif o=='--minAbs':
			rules.append([applyMin,absf,v])
		elif o=='--maxAbs':
			rules.append([applyMax,absf,v])
			
	headers,prestarts=getHeader(filename,headerRow,startRow,fs)
	keys=getCol0ListFromCol1ListStringAdv(headers,keys)
	
	if len(rules)==0:
		print >> stderr, "no rules given. abort"
		printUsageAndExit(programName)
	
	for i in range(0,len(rules)):
		rules[i][2]=getCol0ListFromCol1ListStringAdv(headers,rules[i][2])[0] #only one col!
		
	sortedKeys=[]	
	keyedEntries=dict()
	lino=0
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		if lino<startRow:
			print >> stdout,lin
		else:
			fields=lin.split(fs)
			thisKey=tuple(getSubvector(fields,keys))
			try:
				thisEntry=keyedEntries[thisKey]
			except KeyError:
				thisEntry=[]
				keyedEntries[thisKey]=thisEntry
				sortedKeys.append(thisKey)
				
			thisEntry.append(fields)
	
	fil.close()
	
	#print >> stderr,keyedEntries
	
	for key in sortedKeys:
		thisEntry=keyedEntries[key]
		
		for ruleFunc,convFunc,ruleCol in rules:
			selectedI,selectedValue=ruleFunc(ruleCol,thisEntry,convFunc)
			if len(selectedI)==1:
				#we found one, break
				break
		
		selectedI0=selectedI[0] #if there are still ties, only the first one of the ties are outputed
		#output only this
		print >> stdout,fs.join(thisEntry[selectedI0])