#!/usr/bin/env python

from albertcommon import *
from sys import *
from getopt import getopt

def loadPatternFileToPattenList(patternList,filename,ignoreCase):
	fil=open(filename)
	for lin in fil:
		patternName,pattern=lin.strip().split("\t")
		if ignoreCase:
			patternRegex=re.compile(pattern,re.IGNORECASE)
		else:
			patternRegex=re.compile(pattern)
		patternList.append((patternName,pattern,patternRegex))
	
	fil.close()

def formatHeader(headerName,patternName):
	return headerName+"."+patternName

def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"[options] infile cols > outfile"
	print >> stderr,"find overlapping occurences of regex patterns in strings"
	print >> stderr,"Options:"
	print >> stderr,"--pattern-file filename   append patterns from a pattern list file formatted as lines of <patternName><tab><patternRegex>"
	print >> stderr,"--pattern-named patternName --with-regex regex   append a pattern with patternName and Regex"
	print >> stderr,"--splidar-mode   the intput file is a seq format from splidar program (uses E5,I5,E3,I3, etc to specify subelements)"
	print >> stderr,"--mark-occ   make a column with marking occurences of string, say  pattern [CT]GC[CT] in CTCTTGCT becomes CTCT[TGCT]"
	print >> stderr,"--case-sensitive  regex is case sensative"
	print >> stderr,"--output-density  output density=count/length instead of count"
	
	exit()

def getStringList(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL


def insertString(S,at,I):
	return S[:at]+I+S[at:]

def markOccString(S,locations):
	marker_tuples_loc=dict()	
	for start,end in locations:
		try:
			startendstruct=marker_tuples_loc[start]
		except KeyError:
			startendstruct=[0,0]
			marker_tuples_loc[start]=startendstruct
		startendstruct[0]+=1		
		try:
			startendstruct=marker_tuples_loc[end]
		except KeyError:
			startendstruct=[0,0]
			marker_tuples_loc[end]=startendstruct
		startendstruct[1]+=1
	marker_tuples_loc_sorted=sorted(marker_tuples_loc.keys(),reverse=True)	
	for posAt in marker_tuples_loc_sorted:
		numStarts,numEnds=marker_tuples_loc[posAt]
		S=insertString(S,posAt,"]"*numEnds+"["*numStarts)
	return S


def getCountOrDensity(locations,length,outputDensity):
	if outputDensity:
		return float(len(locations))/length
	else:
		return len(locations)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['pattern-file=','pattern-named=','with-regex=','splidar-mode','mark-occ','case-sensitive','output-density'])
	
	fs="\t"
	splidarMode=False
	patternList=[]
	patternName=""
	startRow=2
	headerRow=1
	ignoreCase=True
	markOcc=False
	outputDensity=False
	
	for o,v in opts:
		if o=='--pattern-file':
			loadPatternFileToPattenList(patternList,v,ignoreCase)
		elif o=='--pattern-named':
			patternName=v
		elif o=='--with-regex':
			if len(patternName)<1:
				print >> stderr,"error: pattern name not set for regex",v
				printUsageAndExit(programName)
			if ignoreCase:
				patternRegex=re.compile(v,re.IGNORECASE)
			else:
				patternRegex=re.compile(v)
			patternList.append((patternName,v,patternRegex))
		elif o=='--splidar-mode':
			splidarMode=True
		elif o=='--case-sensitive':
			ignoreCase=False
		elif o=='--mark-occ':
			markOcc=True
		elif o=='--output-density':
			outputDensity=True
	try:
		infile,cols=args
	except:
		printUsageAndExit(programName)
		
	header,prestarts=getHeader(infile,headerRow,startRow,fs)
	cols=getCol0ListFromCol1ListStringAdv(header,cols)
	
	lino=0
	fil=open(infile)
	for lin in fil:
		lino+=1
		
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		
		
		for col in cols:
			for patternName,pattern,patternRegex in patternList:
				if lino<startRow:
					fields.append(formatHeader(header[col],patternName))
					if markOcc:
						fields.append(formatHeader(header[col],patternName+".mark"))
				else:
					#the real thing here
					if splidarMode:
						elements=fields[col].split("|")
						elementsOut=[]
						occStringOut=[]
						for element in elements:
							#first two letters are name
							elementName=element[0:2]
							if len(elementName)!=2:
								continue
							elementSeq=element[2:]
							locations=RE_findOverlappingInstancesOfCompiledRegex(patternRegex,elementSeq)
							elementsOut.append(elementName+":"+str(getCountOrDensity(locations,len(elementSeq),outputDensity)))
							if markOcc:
								occStringOut.append(elementName+":"+markOccString(elementSeq,locations))
						
						fields.append("|".join(elementsOut))
						if markOcc:
							fields.append("|".join(occStringOut))
					else:
						locations=RE_findOverlappingInstancesOfCompiledRegex(patternRegex,fields[col])
						fields.append(str(getCountOrDensity(locations,len(fields[col]),outputDensity)))
						
						if markOcc:
							fields.append(markOccString(fields[col],locations))						
					
		print >> stdout,fs.join(fields)
	
	
	fil.close()
