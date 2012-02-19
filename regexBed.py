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

from albertcommon import *
from sys import *
from getopt import getopt
from ORFFinder import reverseComplement
from operator import itemgetter

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] infa regex ... > outbed"
	print >> stderr,"options:"
	print >> stderr,"--prefix a. prefix items with a"
	print >> stderr,"--strand (+,-,.). +: only + strand. -: only - strand. .: both strand: default"
	exit(1)


def findAllMatches(seq,regexes):
	matches=[]
	for regex in regexes:
		matches.extend(RE_findOverlappingInstancesOfRegexString(regex,seq))
	
	return matches


def regexBed(chrom,seq,regexes,strand,prefix,startIdx):	

	if seq=="":
		return startIdx
	
	if strand=='-':
		seq=reverseComplement(seq)
	
	matches=findAllMatches(seq,regexes)
	slen=len(seq)
	
	matches=list(set(matches))
	
	if strand=="+":
		matches.sort(key=itemgetter(0))
	elif strand=="-":
		matches.sort(key=itemgetter(1),reverse=True)
	
	
	for match in matches:
		
		
		mstart,mend=match
		if strand=='-':
			x=slen-mend
			y=slen-mstart
			mstart=x
			mend=y
		
		print >> stdout,"%s\t%s\t%s\t%s%d\t0\t%s" %(chrom,mstart,mend,prefix,startIdx,strand)
		
		
		startIdx+=1
		
	
	return startIdx

def regexBedOuter(chrom,seq,regexes,strands,prefix,startIdx):
	if strands=="+":
		return regexBed(chrom,seq,regexes,"+",prefix,startIdx)	
	elif strands=="-":
		return regexBed(chrom,seq,regexes,"-",prefix,startIdx)	
	elif strands==".":
		startIdx=regexBed(chrom,seq,regexes,"+",prefix,startIdx)		
		return regexBed(chrom,seq,regexes,"-",prefix,startIdx)
		
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['prefix=','strand=','upper'])
	
	prefix="match."
	strands="."
	uppercase=False
	startIdx=1
	
	for o,a in opts:
		if o=='--prefix':
			prefix=a
		elif o=='--strand':
			strands=a
			if strands not in ["+","-","."]:
				printUsageAndExit(programName)
		elif o=='--upper':
			uppercase=True
	
	
	if len(args)<2:
		printUsageAndExit(programName)
	
	infa=args[0]
	
	regexes=[]
	
	for ppat in args[1:]:
		regexes.append(ppat)
	
	
	fil=open(infa)
	
	#curLineStart0=0
	chrom=""
	seq=""
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)==0:
			continue
		
		if lin[0]=='>':
			regexBedOuter(chrom,seq,regexes,strands,prefix,startIdx)
			chrom=lin[1:]
			#curLineStart0=0
			seq=""
			
			continue
		
		if uppercase:
			lin=lin.upper()
		
		seq+=lin
		
	
	fil.close()
	regexBedOuter(chrom,seq,regexes,strands,prefix,startIdx)