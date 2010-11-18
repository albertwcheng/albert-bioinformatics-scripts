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
chr1    .       exon    3204563 3207049 .       -       .       ID=Xkr4@EXON5;Parent=Xkr4.aSep07
chr1    .       exon    3195985 3197398 .       -       .       ID=Xkr4@EXON3;Parent=Xkr4.bSep07
chr1    .       exon    3411783 3411982 .       -       .       ID=Xkr4@EXON6;Parent=Xkr4.aSep07
chr1    .       exon    3660633 3661830 .       -       .       ID=Xkr4@EXON7;Parent=Xkr4.aSep07
chr1    .       exon    3203520 3205824 .       -       .       ID=Xkr4@EXON2;Parent=Xkr4.cSep07
chr1    .       exon    3203690 3206425 .       -       .       ID=Xkr4@EXON4;Parent=Xkr4.bSep07
chr1    .       exon    3195864 3197398 .       -       .       ID=Xkr4@EXON1;Parent=Xkr4.cSep07

cares about exon only

to something like that 

LOC653333@EXON49_LOC653333@EXON50_LOC653333@EXON51_LOC653333@EXON52_LOC653333@EXON53_LOC653333@EXON54

'''
from os.path import *
from sys import *


def getAttributes(attrString):
	attributes=dict()
	items=attrString.split(";")
	for item in items:
		key,values=item.split("=")
		values=values.split(",")
		attributes[key]=values
	
	return attributes
		
def printUsageAndExit(programName):
	print >> stderr,programName,"filename > ofilename"
	print >> stderr,"description: makes MISO style exon string from gff file"
	exit()

if __name__=='__main__':
	programName=basename(argv[0])
	args=argv[1:]
	try:
		filename,=args
	except:
		printUsageAndExit(programName)	
		
		
	transcriptExonDict=dict() #[transcriptName][exonStart]=exonID
	
	
	print >> stdout,"transcript\tisoforms"
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=='#':
			continue
		
		fields=lin.split("\t")
		elementType=fields[2]
		if elementType != "exon":
			continue
		attrString=fields[8]
		attributes=getAttributes(attrString)
		
		gStart=int(fields[3])
		
		
		try:
			exonID=attributes["ID"][0]
		except:
			print >> stderr,"An exon without ID. abort",lin
			exit()
		
		#ID is the exon name, parent the transcript name
		try:
			transcriptNamesForThisExon=attributes["Parent"]
		except:
			#What!! Not parent?
			print >> stderr,"An exon without parent. abort",lin
			exit()
		
		for transcriptID in transcriptNamesForThisExon:
			try:
				exonDictForTranscript=transcriptExonDict[transcriptID]
			except KeyError:
				exonDictForTranscript=dict()
				transcriptExonDict[transcriptID]=exonDictForTranscript
			
			if gStart in exonDictForTranscript:
				print >> stderr,"Panic: exon start repeated for a particular transcript. abort",lin
				exit()
			
			exonDictForTranscript[gStart]=exonID
	
	fil.close()
	
	#now output
	for transcriptID,exonDictForTranscript in transcriptExonDict.items():
		exonStartsSorted=exonDictForTranscript.keys()
		exonStartsSorted.sort()
		exonNameSplits=[]
		for eStart in exonStartsSorted:
			exonNameSplits.append(exonDictForTranscript[eStart])
		
		print >> stdout,transcriptID+"\t"+"_".join(exonNameSplits)
	
	
	
