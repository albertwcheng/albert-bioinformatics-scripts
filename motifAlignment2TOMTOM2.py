#!/usr/bin/python

from sys import *


def outputTOMTOM(sequences,includeAlphabet):
	nCols=len(sequences[0])
	nRows=len(sequences)
	ntDict={"A":[],"C":[],"T":[],"G":[]}
	
	for col in range(0,nCols):
		A_count=0
		C_count=0
		G_count=0
		T_count=0
		for row in range(0,nRows):
			N=sequences[row][col].upper()
			if N=='A':
				A_count+=1
			elif N=='C':
				C_count+=1
			elif N=='G':
				G_count+=1
			elif N=='T':
				T_count+=1
			else:
				print >> stderr,"unknown character",N,"found. abort"
				exit()
		
		ntDict["A"].append(str(A_count))
		ntDict["C"].append(str(C_count))
		ntDict["G"].append(str(G_count))
		ntDict["T"].append(str(T_count))

	for nt in ["A","C","G","T"]:
		if includeAlphabet:
			print >> stdout,"\t".join([nt]+ntDict[nt])
		else:
			print >> stdout,"\t".join(ntDict[nt])
		
	
			
	

def readSequences(filename):
	fil=open(filename)
	sequences=[]
	thisSeq=""
	for lin in fil:
		lin=lin.rstrip()
		if lin[0]=='>':
			if len(thisSeq)>0:
				sequences.append(thisSeq)
			thisSeq=""
			continue
		
		thisSeq+=lin
		
	
	fil.close()
	if len(thisSeq)>0:
		sequences.append(thisSeq)
	
	return sequences	
		
def printUsageAndExit(programName):
	print >> stderr,programName,"[--include-alphabet] fastafile"
	exit()
	
if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	includeAlphabet=False
	try:
		if len(args)==2:
			swi,filename=args
			if swi=="--include-alphabet":
				includeAlphabet=True
			else:
				print >> stderr,"unknown option",swi
				printUsageAndExit(programName)		
		else:

			filename,=args
			if filename[0:2]=="--":
				printUsageAndExit(programName)
	except:
		printUsageAndExit(programName)
		
	sequences=readSequences(filename)
	outputTOMTOM(sequences,includeAlphabet)
