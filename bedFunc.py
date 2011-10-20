#!/usr/bin/env python

def genomicCoordToTranscriptCoordBedFormatted(gStart,blockStarts,blockLengths,coord0,reverse=False):
	cumlength=0
	coordRelGStart=coord0-gStart
	for blockStart,blockLength in zip(blockStarts,blockLengths):
		if coordRelGStart>=blockStart and coordRelGStart<blockStart+blockLength:
			coordForward=cumlength+coordRelGStart-blockStart
			if reverse:
				return sum(blockLengths)-coordForward-1
			else:
				return coordForward
		
		cumlength+=blockLength
	
	return None
	
def transcriptCoordToGenomicCoordBedFormatted(gStart,blockStarts,blockLengths,coord0,reverse=False):
	cumlength=0
	if reverse:
		for i in range(len(blockStarts)-1,-1,-1):
			blockStart=blockStarts[i]
			blockLength=blockLengths[i]
			if cumlength<=coord0 and coord0<cumlength+blockLength:
				return gStart+blockStart+blockLength-1-coord0+cumlength
			
			cumlength+=blockLength
	
	else:
		for blockStart,blockLength in zip(blockStarts,blockLengths):
			if cumlength<=coord0 and coord0<cumlength+blockLength:
				return gStart+blockStart+coord0-cumlength
			cumlength+=blockLength
	
	return None
	
def isBoundValid2(start0,end1):
	return start0>=0 and end1>=1 and end1>start0
	
	
def isBoundValid(bound):
	return isBoundValid2(bound[0],bound[1])

def clipBlocksByGenomicBound(gStart,blockStarts,blockLengths,gCoordStart0,gCoordEnd1,setFirstBlockStartZero=False):
	clipStarts0=[]
	clipSizes=[]
	gCoordStartRelgStart0=gCoordStart0-gStart
	gCoordEndRelgStart1=gCoordEnd1-gStart
	
	firstBlockStartOffset=0
	
	for blockStart0,blockLength in zip(blockStarts,blockLengths):
		blockEnd1=blockStart0+blockLength
		potentialBound=(max(gCoordStartRelgStart0,blockStart0),min(gCoordEndRelgStart1,blockEnd1))
		if isBoundValid(potentialBound):
			if setFirstBlockStartZero and len(clipStarts0)==0:
				firstBlockStartOffset=potentialBound[0]
				
			clipStarts0.append(potentialBound[0]-firstBlockStartOffset)
			clipSizes.append(potentialBound[1]-potentialBound[0])
	
	return clipStarts0,clipSizes		
	


if __name__=='__main__':
	print "test bedFunc.py subroutines"
	
	gStart=0
	blockStarts=[0,8,20]
	blockSizes=[5,7,2]
	
	print "genomic->transcript forward"
	for i in range(-1,22):
		print "genomic",i,":","transcript foward",genomicCoordToTranscriptCoordBedFormatted(gStart,blockStarts,blockSizes,i)
	
	print "genomic->transcript reverse"
	for i in range(-1,22):
		print "genomic",i,":","transcript foward",genomicCoordToTranscriptCoordBedFormatted(gStart,blockStarts,blockSizes,i,True)
		
	print "transcript forward->genomic"
	for i in range(-1,14):
		print "transcript forward",i,":","genomic",transcriptCoordToGenomicCoordBedFormatted(gStart,blockStarts,blockSizes,i)
		
	print "transcript reverse->genomic"
	for i in range(-1,14):
		print "transcript forward",i,":","genomic",transcriptCoordToGenomicCoordBedFormatted(gStart,blockStarts,blockSizes,i,True)	
		
		
	print clipBlocksByGenomicBound(gStart,blockStarts,blockSizes,3,21)
	print clipBlocksByGenomicBound(gStart,blockStarts,blockSizes,3,21,True)
		
	print clipBlocksByGenomicBound(gStart,blockStarts,blockSizes,50,21)
	
	print clipBlocksByGenomicBound(gStart,blockStarts,blockSizes,8,15)	