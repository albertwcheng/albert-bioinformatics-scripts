#!/usr/bin/python

#simpleBedOverlap.py
from sys import *

def readBed(filename,warnduplicate=True):
	#return Bed[chrom]=[dict((start,stop))=[[field4,...]]
	fil=open(filename)
	Bed=dict()
	for lin in fil:
		lin=lin.rstrip()
		fields=lin.split("\t")
		if len(fields)<3:
			continue

		try:
			chrom,start,end=fields[0:3]
			if len(fields)>3:
				more=fields[3:]
			else:
				more=[]
			start=int(start)
			end=int(end)
		except:
			#invalid formatted line: ignore
			continue
		
		try:
			chromDict=Bed[chrom]
		except:
			chromDict=dict()
			Bed[chrom]=chromDict

		#assume no same entry:
		if warnduplicate and (start,end) in chromDict:
			print >> stderr,"Warning: %s (%d,%d] has duplicate entries. Only the last one entry is used" %(filename,start,end)

		chromDict[(start,end)]=more

	fil.close()
	
	return Bed

def isValid(coord):
	if coord[0]>=0 and coord[1]>coord[0]:
		return True

	return False

def overlapBound(coord1,coord2):
	newBound=(max([coord1[0],coord2[0]]),min([coord1[1],coord2[1]]))
	return newBound

def addBedEntry(bed,chrom,start,end,more):
	try:
		chromDict=bed[chrom]
	except:
		chromDict=dict()
		bed[chrom]=chromDict
	
	chromDict[(start,end)]=more


def overlapPiecesOfIntervals(Bed1,Bed2):
	#foreach of Bed1 chr
	newBed=dict()

	for Bed1Chr,Bed1ChromDict in Bed1.items():
		print >> stderr,"processing bed1chr",Bed1Chr
		try:		
			Bed2ChromDict=Bed2[Bed1Chr]
		except:
			continue
		
		#now pairwise bruteforce!
		for coord1,more1 in Bed1ChromDict.items():
			for coord2,more2 in Bed2ChromDict.items():		
				ob=overlapBound(coord1,coord2)
				if isValid(ob):
					addBedEntry(newBed,Bed1Chr,ob[0],ob[1],more1+more2)
	return newBed


def binIntv(Bed1,binInterval):
	bins=dict()
	for Bed1Chrom,chromDict in Bed1.items():
		binsChromDict=dict()
		bins[Bed1Chrom]=binsChromDict
		for coord in chromDict.keys():
			start,end=coord
			binKey1=start/binInterval
			binKey2=end/binInterval

			#now add binKey1
			try:
				binSet=binsChromDict[binKey1]
			except:
				binSet=set()
				binsChromDict[binKey1]=binSet

			binSet.add(coord)

			if binKey2!=binKey1: #span more than 1 bin
				for binK in range(binKey1+1,binKey2+1):
					try:
						binSet=binsChromDict[binK]
					except:
						binSet=set()
						binsChromDict[binK]=binSet

					binSet.add(coord)

	return bins

def overlapPiecesOfIntervalsByBins(bin1,bin2,bed1,bed2):
	#foreach of Bed1 chr
	newBed=dict()
	em=[]
	for bin1Chr,bin1ChromDict in bin1.items():
		print >> stderr,"processing bin1chr",bin1Chr,
		try:		
			bin2ChromDict=bin2[bin1Chr]
		except:
			continue
		
		bed1ChromDict=bed1[bin1Chr]
		bed2ChromDict=bed2[bin1Chr]

		#for each bin in bin1
		for bkey1,b1 in bin1ChromDict.items():
			try:
				b2=bin2ChromDict[bkey1]
			except:
				continue
			
			#now pairwise bruteforce in each bin set
			for coord1 in b1:
				for coord2 in b2:		
					ob=overlapBound(coord1,coord2)
				
					if isValid(ob):
						addBedEntry(newBed,bin1Chr,ob[0],ob[1],bed1ChromDict[coord1]+bed2ChromDict[coord2]+list(coord1)+list(coord2))

	return newBed


def toStrArray(L):
	oL=[]
	for s in L:
		oL.append(str(s))
	return oL

def printBed(stream,bed):
	for bedchrom,chromdict in bed.items():
		for coord,more in chromdict.items():
			print >> stream,"\t".join(toStrArray([bedchrom]+list(coord)+more))


def printUsageAndExit(programName):
	print >> stderr,programName,"bedfile1 bedfile2"
	exit()

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		bedfile1,bedfile2=args
	except:
		printUsageAndExit(programName)

	binInterval=100000

	print >> stderr,"reading in",bedfile1
	bed1=readBed(bedfile1)
	print >> stderr,"reading in",bedfile2
	bed2=readBed(bedfile2)
	print >> stderr,"making bins"
	bin1=binIntv(bed1,binInterval)
	#print >> stderr,bin1
	bin2=binIntv(bed2,binInterval)
	#print >> stderr,bin2
	print >> stderr,"overlap...",
	obed=overlapPiecesOfIntervalsByBins(bin1,bin2,bed1,bed2)
	#obed=overlapPiecesOfIntervals(bed1,bed2)
	print >> stderr,"... done."
	print >> stderr,"printing"
	printBed(stdout,obed)
	
	
