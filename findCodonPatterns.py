#!/usr/bin/env python2.7


from sys import *

def getIDName(DNAname):
	ID=DNAname.split("cdna")[0].strip()
	try:
		geneName=DNAname.split("gene_symbol:")[1]
		geneName=geneName.split(" ")[0].strip()
	except:
		geneName=ID
	
	return (ID,geneName)


def patternMatchBase(x,y): #x is pattern
	y=y.upper()
	if x=='N': #match anything
		return True
	if x==y:
		return True
	if x=='a' and y!='A':
		return True
	if x=='c' and y!='C':
		return True
	if x=='g' and y!='G':
		return True
	if x=='t' and y!='T':
		return True
	if x=='M' and y in ['A','C']:
		return True
	if x=='R' and y in ['A','G']:
		return True
	if x=='W' and y in ['A','T']:
		return True
	if x=='S' and y in ['C','G']:
		return True
	if x=='Y' and y in ['C','T']:
		return True
	if x=='K' and y in ['G','T']:
		return True
	if x=='V' and y in ['A','C','G']:
		return True
	if x=='H' and y in ['A','C','T']:
		return True
	if x=='D' and y in ['A','G','T']:
		return True
	if x=='B' and y in ['C','G','T']:
		return True
	


	return False

def processSeq(DNAname,DNAseq,patterns):
	if DNAseq=="":
		return
	longestORF=DNAseq
	longestORFLength=len(DNAseq)

	for pattern in patterns:
		patternLength=len(pattern)
		for i in range(0,longestORFLength-patternLength,3):
			matched=False
			for j in range(0,patternLength):
				if not patternMatchBase(pattern[j],longestORF[i+j]):
					break
				elif j==patternLength-1:
					#matched:
					matched=True
			
			if matched:
				print >> stdout,pattern+"\t"+DNAname+"\t"+str(i+1)+"\t"+longestORF[:i].lower()+longestORF[i:i+patternLength].upper()+longestORF[i+patternLength:].lower()


def processQItem(prePatterns,queue,U,patterns):
	currentString,level=U
	minRep,maxRep,subPattern=prePatterns[level]
	thisPatternUnfolded=""
	for i in range(1,maxRep+1):
		thisPatternUnfolded+=subPattern
		if i>=minRep:
			if level==len(prePatterns)-1: #last, yield patterns
				patterns.append(currentString+thisPatternUnfolded)
			else:
				queue.append([currentString+thisPatternUnfolded,level+1])


def generatePatterns(patternString):
	patterns=[]
	prePatterns=[]
	for subPattern in patternString.split(","):
		if ":" in subPattern:
			left,right=subPattern.split(":")
			minRep,maxRep=left.split("-")
			prePatterns.append([int(minRep),int(maxRep),right])
		else:
			prePatterns.append([1,1,subPattern])
	
	queue=[["",0]]
	while len(queue)>0:
		U=queue.pop(0)
		processQItem(prePatterns,queue,U,patterns)

	return patterns




def printUsageAndExit(programName):
	print >> stderr,programName,"filename colName colCDS pattern"
	print >> stderr,"pattern length has to be multiple of 3"
	print >> stderr,"A = Adenine"
	print >> stderr,"C = Cytosine"
	print >> stderr,"G = Guanine"
	print >> stderr,"T = Thymine"
	print >> stderr,"a = not A"
	print >> stderr,"c = not C"
	print >> stderr,"g = not G"
	print >> stderr,"t = not T"
	exit(1)



if __name__=='__main__':
	programName=argv[0]
	try:
		filename=argv[1]
		colName=int(argv[2])-1
		colCDS=int(argv[3])-1
		patternString=argv[4]	
	except:
		printUsageAndExit(programName)
	

	patterns=generatePatterns(patternString)

	print >> stderr,"%d patterns generated from %s" %(len(patterns),patternString)

	for i in range(0,len(patterns)):
		pattern=patterns[i]
		print >> stderr,(i+1),pattern
		if len(pattern)%3!=0:
			print >> stderr,"Error: %s len=%d pattern length has to be multiple of 3" %(pattern,len(pattern))
			printUsageAndExit(programName)
	

	DNAname=""
	DNAseq=""
	fil=open(filename)
	lino=0
	for lin in fil:
		lino+=1
		#test break
		#if lino==1000:
		#	break
		
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
		CDSname=fields[colName]
		CDSseq=fields[colCDS]

		processSeq(CDSname,CDSseq,patterns)

			


	fil.close()	
	
	
	

		