#!/usr/bin/env python2.7

'''
genetic code copied from 
Beginning Python for Bioinformatics
a step-by-step guide to create Python applications in bioinformatics
http://python.genedrift.org/2007/04/19/genetic-code-part-i/
'''

from albertcommon import *
from sys import *

gencode = {
    'ATA':'I',    #Isoleucine
    'ATC':'I',    #Isoleucine
    'ATT':'I',    # Isoleucine
    'ATG':'M',    # Methionine
    'ACA':'T',    # Threonine
    'ACC':'T',    # Threonine
    'ACG':'T',    # Threonine
    'ACT':'T',    # Threonine
    'AAC':'N',    # Asparagine
    'AAT':'N',    # Asparagine
    'AAA':'K',    # Lysine
    'AAG':'K',    # Lysine
    'AGC':'S',    # Serine
    'AGT':'S',    # Serine
    'AGA':'R',    # Arginine
    'AGG':'R',    # Arginine
    'CTA':'L',    # Leucine
    'CTC':'L',    # Leucine
    'CTG':'L',    # Leucine
    'CTT':'L',    # Leucine
    'CCA':'P',    # Proline
    'CCC':'P',    # Proline
    'CCG':'P',    # Proline
    'CCT':'P',    # Proline
    'CAC':'H',    # Histidine
    'CAT':'H',    # Histidine
    'CAA':'Q',    # Glutamine
    'CAG':'Q',    # Glutamine
    'CGA':'R',    # Arginine
    'CGC':'R',    # Arginine
    'CGG':'R',    # Arginine
    'CGT':'R',    # Arginine
    'GTA':'V',    # Valine
    'GTC':'V',    # Valine
    'GTG':'V',    # Valine
    'GTT':'V',    # Valine
    'GCA':'A',    # Alanine
    'GCC':'A',    # Alanine
    'GCG':'A',    # Alanine
    'GCT':'A',    # Alanine
    'GAC':'D',    # Aspartic Acid
    'GAT':'D',    # Aspartic Acid
    'GAA':'E',    # Glutamic Acid
    'GAG':'E',    # Glutamic Acid
    'GGA':'G',    # Glycine
    'GGC':'G',    # Glycine
    'GGG':'G',    # Glycine
    'GGT':'G',    # Glycine
    'TCA':'S',    # Serine
    'TCC':'S',    # Serine
    'TCG':'S',    # Serine
    'TCT':'S',    # Serine
    'TTC':'F',    # Phenylalanine
    'TTT':'F',    # Phenylalanine
    'TTA':'L',    # Leucine
    'TTG':'L',    # Leucine
    'TAC':'Y',    # Tyrosine
    'TAT':'Y',    # Tyrosine
    'TAA':'_',    # Stop
    'TAG':'_',    # Stop
    'TGC':'C',    # Cysteine
    'TGT':'C',    # Cysteine
    'TGA':'_',    # Stop
    'TGG':'W',    # Tryptophan
}


def complement(c):
	if c=="A":
		return "T"
	elif c=="a":
		return "t"
	elif c=="C":
		return "G"
	elif c=="c":
		return "g"
	elif c=="G":
		return "C"
	elif c=="g":
		return "c"
	elif c=="T":
		return "A"
	elif c=="t":
		return "a"
	elif c=="U":
		return "A"
	elif c=="u":
		return "a"
	else:
		return c

def reverseComplement(seq):
	rc=""
	for i in range(len(seq)-1,-1,-1):
		rc+=complement(seq[i])
	
	return rc

def findORFInThreeFrames(seq,findLongestORFs=True,minORFLength=-1,maxORFLength=-1,startCodonsUpper=["ATG"],stopCodonsUpper=["TAA","TAG","TGA"]):
	
	seq=seq.upper()
	
	starts=[]
	for startCodon in startCodonsUpper:
		starts+=String_findAll(seq,startCodon)
	
	ends=[]
	for stopCodon in stopCodonsUpper:
		ends+=String_findAll(seq,stopCodon)
	
	features=starts+ends
	features.sort()
	
	#print >> stderr,features
	
	phaseATG=[-1,-1,-1]
	
	longestORFLength=-1
	longestORFRange=None
		
	for feature in features:
		featurePhase=feature%3
		if seq[feature:feature+3] in startCodonsUpper:
			#its a start
			#if this phase is not marked with an current open ORF, then set it
			if phaseATG[featurePhase]==-1:
				phaseATG[featurePhase]=feature
		else:
			#its an end
			#if this phase is open, then see if longer than available and then close it, if phase is not open, forget it. 
			thisPhaseATG=phaseATG[featurePhase]
			phaseATG[featurePhase]=-1
			if thisPhaseATG!=-1:
				#open!
				
				
				thisORFLength=(feature-thisPhaseATG)/3
				
				if minORFLength>0 and thisORFLength<minORFLength:
					continue
				
				if maxORFLength>0 and thisORFLength>maxORFLength:
					continue

				if findLongestORFs:
					if thisORFLength>longestORFLength:
						longestORFLength=thisORFLength
						longestORFRange=[[thisPhaseATG,feature]]
					elif thisORFLength==longestORFLength:
						longestORFRange.append([thisPhaseATG,feature])
				else:
					if longestORFRange==None:
						longestORFRange=[]
					longestORFRange.append([thisPhaseATG,feature])
					
	return longestORFRange

def findLongestORFInThreeFrames(seq,minORFLength=-1,maxORFLength=-1,startCodonsUpper=["ATG"],stopCodonsUpper=["TAA","TAG","TGA"]):
	return findORFInThreeFrames(seq,True,minORFLength,maxORFLength,startCodonsUpper,stopCodonsUpper)

def getReverseComplementCoordNegRepresentation(rang):
	return [-rang[0]-1,-rang[1]]

def getReverseComplementCoordNegRepresentationForRanges(ranges):
	ret=[]
	for rang in ranges:
		ret.append(getReverseComplementCoordNegRepresentation(rang))
	return ret

def getSequencesFromRanges(seq,ranges,includeStopCodon=False):
	seqs=[]
	rc=None
	if includeStopCodon:
		includeStopCodon=3
	else:
		includeStopCodon=0
		
	if ranges==None:
		return None
	for rang in ranges:
		if rang[0]>=0:
			#in positive strand
			seqs.append(seq[rang[0]:rang[1]+includeStopCodon])
		else:
			#in negative strand
			if rc==None:
				rc=reverseComplement(seq)
			
			seqs.append(rc[-rang[0]-1:-rang[1]+includeStopCodon])
			
	return seqs
			
def findORFInSixFrames(seq,findLongestORFs=True,minORFLength=-1,maxORFLength=-1,startCodonsUpper=["ATG"],stopCodonsUpper=["TAA","TAG","TGA"]):
	forwardRange=findORFInThreeFrames(seq,findLongestORFs,minORFLength,maxORFLength,startCodonsUpper,stopCodonsUpper)
	rc=reverseComplement(seq)
	#print >> stderr,"rc=",rc
	backwardRange=findORFInThreeFrames(rc,findLongestORFs,minORFLength,maxORFLength,startCodonsUpper,stopCodonsUpper,)
	
	if forwardRange==None and backwardRange==None:
		return None
	
	if findLongestORFs:
		if forwardRange:
			forwardLength=forwardRange[0][1]-forwardRange[0][0]
		else:
			forwardLength=-1
	
		if backwardRange:
			backwardLength=backwardRange[0][1]-backwardRange[0][0]
		else:
			backwardLength=-1
		
		if forwardLength>backwardLength:
			#print >> stderr,"here3"
			return forwardRange
		elif forwardLength==backwardLength:
			#print >> stderr,"here2"
			return forwardRange+getReverseComplementCoordNegRepresentationForRanges(backwardRange)
		else:
			#print >> stderr,"here"
			return getReverseComplementCoordNegRepresentationForRanges(backwardRange)
	else:
		returna=[]
		if forwardRange!=None:
			returna.extend(forwardRange)
		
		if backwardRange!=None:
			returna.extend(getReverseComplementCoordNegRepresentationForRanges(backwardRange))
		
		return returna
			
def findLongestORFInSixFrames(seq,startCodonsUpper=["ATG"],stopCodonsUpper=["TAA","TAG","TGA"],minORFLength=-1,maxORFLength=-1):
	return findORFInSixFrames(seq,True,minORFLength,maxORFLength,startCodonsUpper,stopCodonsUpper)

def DNA2Protein(seq):
	aaSeq=""
	for i in range(0,len(seq),3):
		aaSeq+=gencode[seq[i:i+3]]
	return aaSeq.replace("_","")

if __name__=='__main__':

	programName=argv[0]
	args=argv[1:]
	try:
		sequence,longest=args
	except:
		print >> stderr,programName,"sequence <longest,all>"
		exit(1)
		
	ranges=findORFInSixFrames(sequence,longest=="longest")
	seqs=getSequencesFromRanges(sequence,ranges,True)
	if ranges!=None:
		for r,s in zip(ranges,seqs):
			print >> stdout,r,s