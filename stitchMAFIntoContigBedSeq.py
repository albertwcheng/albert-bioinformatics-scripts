#!/usr/bin/python

from sys import *


def fillArrayUpToWith(L,nElements,withElement):
	diffL=nElements-len(L)
	if diffL>=1:
		for i in range(0,diffL):
			L.append(withElement)

def printUsageAndExit(programName):
	print >> stderr,programName,"mafFile genomes(,) > bedFile"
	exit()
	
	
def outBedEntry(bedEntry,prevStart,prevLen):

	if len(bedEntry)<3:
		return
		
	#now you need to reprocess the bedEntry
	chrom=bedEntry[0]
	start=bedEntry[1]
	if len(bedEntry)<2+1:
		return
		
	refSeqLength=len(bedEntry[2])
	end=prevStart+prevLen
	
	#again make sure same length
	for i in range(3,len(bedEntry)):
		bedEntry[i]=fillStringUpToWith(bedEntry[i],refSeqLength,"-") #fill the gap	
		
	bedEntry=[chrom,str(start),str(end)]+bedEntry[2:]
	print >> stdout,"\t".join(bedEntry)
	
	
def fillStringUpToWith(S,length,withChr):
	diffL=length-len(S)
	if diffL<0:
		raise ValueError
	
	for i in range(0,diffL):
		S=S+withChr
	
	return S
	
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		mafFile,genomes=args
	except:
		printUsageAndExit(programName)
	
	fil=open(mafFile)
	
	nextOneNeeded=False
	
	genomes=genomes.split(",")
	
	genomesToIndx=dict()
	for i in range(0,len(genomes)):
		genomesToIndx[genomes[i]]=i+2
	
	
	#bedEntry=[chr,start,seq1,seq2,...seqN]
	bedEntry=["",0]
	
	prevChrom=""
	prevStart=-1000
	prevLen=-1000
	
	
	bedEntries=[]
	
	print >> stdout,"#chrom\tstart\tend\t"+"\t".join(genomes)	
	
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue
			
		fields=lin.split()
		
		if fields[0]=='a':
			#the next one is the one of interest
			nextOneNeeded=True
			#but now, make sure everything is in sync
			if len(bedEntry)>2: 
				refSeqLength=len(bedEntry[2])
				#fill every other seq up to this length
				for i in range(3,len(bedEntry)):
					bedEntry[i]=fillStringUpToWith(bedEntry[i],refSeqLength,"-") #fill the gap
				
		elif fields[0]=='s':
			thisGenome,thisChrom=fields[1].split(".")
			thisStart=int(fields[2])
			thisLen=int(fields[3])
			thisSeq=fields[6]
			if nextOneNeeded:
				if thisGenome!=genomes[0]:
					print >> stderr,"Error: the reference genome is not the first in the block"
					exit()
			
				nextOneNeeded=False
				#if prevChrom==thisChrom and thisStart<prevStart+prevLen:
				#	print >> stderr,"maf file block not sorted. abort",thisStart,prevStart+prevLen
				#	exit()
				
				#need to start new bed entry?
				if prevChrom!=thisChrom or prevStart+prevLen!=thisStart:
					#remember curr bedEntry:
					outBedEntry(bedEntry,prevStart,prevLen)
					#start new!
					bedEntry=[thisChrom,thisStart]
					fillArrayUpToWith(bedEntry,len(genomes)+2,"")
					
				prevChrom=thisChrom
				prevStart=thisStart
				prevLen=thisLen
					
			try:
				colIndx=genomesToIndx[thisGenome]
			except KeyError:
				continue #this genome is not specified, ignore
			
			bedEntry[colIndx]+=thisSeq
			
	fil.close()
	
	outBedEntry(bedEntry,prevStart,prevLen)


	
		
		