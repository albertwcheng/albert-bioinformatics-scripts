#!/usr/bin/python

'''

get overlapping pieces of intervals from two bed files.

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

###NOT YET TESTED COMPLETE COMPATIBILITY WITH GALAXY


from sys import *
from getopt import getopt

def lengthOfBound(coord):
	return max([0,coord[1]-coord[0]])

def readBed(filename,appenduplicate,warnduplicate):
	#return Bed[chrom]=[dict((start,stop))=[[field4,...]]
	fil=open(filename)
	Bed=dict()
	for lin in fil:
		lin=lin.rstrip()
		fields=lin.split("\t")
		if len(fields)<3:
			continue

		if fields[0][0]=='#':
			#commented line. ignore
			continue

		try:
			chrom,start,end=fields[0:3]
			if len(fields)>3:
				more=fields[3:]
			else:
				more=[]

			more=tuple(more)

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
			if not appenduplicate:
				extra="Only the last item was used"
			else:
				extra=""
			print >> stderr,"Warning: %s (%d,%d] has duplicate entries.%s" %(filename,start,end,extra)

		if appenduplicate and (start,end) in chromDict:

			chromDict[(start,end)].append(more)
		else:
			chromDict[(start,end)]=[more]

	fil.close()
	
	return Bed

def isValid(coord):
	if coord[0]>=0 and coord[1]>coord[0]:
		return True

	return False

def overlapBound(coord1,coord2):
	newBound=(max([coord1[0],coord2[0]]),min([coord1[1],coord2[1]]))
	return newBound


def addBedEntry2(bed,chrom,start,end,more,appenduplicate,warnduplicate,bed1entrydict,bed1coord):
	try:
		chromDict=bed[chrom]
	except:
		chromDict=dict()
		bed[chrom]=chromDict
	
	if warnduplicate and (start,end) in chromDict:
		if not appenduplicate:
			extra="Only the last item was used"
		else:
			extra=""
		print >> stderr,"Warning: %s (%d,%d] has duplicate entries.%s" %(filename,start,end,extra)

	if appenduplicate and (start,end) in chromDict:
		chromDict[(start,end)].add(more)
	else:
		chromDict[(start,end)]=set([more])

	bed1start,bed1end=bed1coord
	#moreSet=chromDict[(start,end)]
	try:
		bed1entrydict[(bed1start,bed1end)].add((start,end))
	except KeyError:
		bed1entrydict[(bed1start,bed1end)]=set([(start,end)])

def addBedEntry(bed,chrom,start,end,more,appenduplicate,warnduplicate):
	try:
		chromDict=bed[chrom]
	except:
		chromDict=dict()
		bed[chrom]=chromDict
	
	if warnduplicate and (start,end) in chromDict:
		if not appenduplicate:
			extra="Only the last item was used"
		else:
			extra=""
		print >> stderr,"Warning: %s (%d,%d] has duplicate entries.%s" %(filename,start,end,extra)

	if appenduplicate and (start,end) in chromDict:
		chromDict[(start,end)].add(more)
	else:
		chromDict[(start,end)]=set([more])
	
	

''' replaced by the binwise overlap
def overlapPiecesOfIntervals(Bed1,Bed2,appenduplicate,warnduplicate):
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
					for m1 in more1:
						for m2 in more2:
							addBedEntry(newBed,Bed1Chr,ob[0],ob[1],m1+m2,appenduplicate,warnduplicate)
	return newBed
'''

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


def updateOverlapGraph(overlapgraph,visited,bincontent):
	for i in range(0,len(bincontent)-1):
		for j in range(i+1,len(bincontent)):
			coord1=bincontent[i]
			coord2=bincontent[j]
			ob=overlapBound(coord1,coord2)
			if isValid(ob): #overlapped! connect them!
				#connect
				try:
					coord1adjlist=overlapgraph[coord1]
				except:
					coord1adjlist=set()
					overlapgraph[coord1]=coord1adjlist
					visited[coord1]=False
				
				try:
					coord2adjlist=overlapgraph[coord2]
				except:
					coord2adjlist=set()
					overlapgraph[coord2]=coord2adjlist
					visited[coord2]=False

				coord1adjlist.add(coord2)
				coord2adjlist.add(coord1)



def expandBoundInPlace(expandee,expander):
	expandee[0]=min(expandee[0],expander[0])
	expandee[1]=max(expandee[1],expander[1])

def overlapGraph2MergedRegions(overlapgraph,visited,nodes):
	regions=[]
	for S in nodes:
		
		if S not in visited:
			#singleton
			regions.append([list(S),set([S])])	
		else:
			if visited[S]:
				continue
			
					
			
			mergedBound=list(S)						
			boundmembers=set()	
			regions.append([mergedBound,boundmembers])	
			
			Q=[S]
			#now traverse the network from u
			while len(Q)>0:
				u=Q.pop(0)
				expandBoundInPlace(mergedBound,u)
				visited[u]=True	
				boundmembers.add(u)
				#now go to neighbors
				V=overlapgraph[u]
				for v in V:
					if not visited[v]:
						Q.append(v)
	
	return regions
				
def mergeIntervals(bin,bed):
	
	newBed=dict()
	for binchr,binchromdict in bin.items():
		chromdict=dict()
		newBed[binchr]=chromdict
		print >> stderr,"processing binchr",binchr
		overlapgraph=dict() #overlap within a chr only
		visited=dict()
		bedchromdict=bed[binchr]
		coordsset=bedchromdict.keys()
		
		for bkey,bincontent in binchromdict.items():
			#pass ##here ###continue here!!!
			updateOverlapGraph(overlapgraph,visited,list(bincontent))

		#print >> stderr,"overlapG",overlapgraph
		#print >> stderr,"visited",visited
		#now we have an overlap graph
		regions=overlapGraph2MergedRegions(overlapgraph,visited,coordsset)
		#print >> stderr,"regions",regions
		#for region
		for newMergedBound,setOfOrigBounds in regions:
			chromdict[tuple(newMergedBound)]=tuple(tuple())	
	
	return newBed

def overlapPiecesOfIntervalsByBins(bin1,bin2,bed1,bed2,appenduplicate,warnduplicate,overlaplength,addChromIfNeeded,collapsePerBed1,mergeBed1All,mb1allbinIntv):
	#foreach of Bed1 chr
	newBed=dict()
	em=[]
	for bin1Chr,bin1ChromDict in bin1.items():
		print >> stderr,"processing bin1chr",bin1Chr,
		try:		
			bin2ChromDict=bin2[bin1Chr]
		except:
			if addChromIfNeeded:
				bin2haschr=(bin2.keys()[0][0:3].lower()=='chr')
				bin1haschr=(bin1Chr[0:3].lower()=='chr')
				if (bin1haschr or bin2haschr) and (not (bin1haschr and bin2haschr)): #inconsistent chr label
					if bin1haschr:
						bin2Chr=bin1Chr[3:]
					else:
						bin2Chr=bin2.keys()[0][0:3]+bin1Chr
					
					try: #now try again:
						bin2ChromDict=bin2[bin2Chr]
					except:
						continue
				else:
					continue
			else:
				continue
		
		bed1ChromDict=bed1[bin1Chr]
		bed2ChromDict=bed2[bin1Chr]
		bed1entrydict=dict()

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
				
					if isValid(ob) and lengthOfBound(ob)>=overlaplength:
						more1=bed1ChromDict[coord1]
						more2=bed2ChromDict[coord2]
						for m1 in more1:
							for m2 in more2:
								addBedEntry2(newBed,bin1Chr,ob[0],ob[1],m1+m2+coord1+coord2,appenduplicate,warnduplicate,bed1entrydict,coord1)
		

		
		#now collapsing maybe?
		if collapsePerBed1 or mergeBed1All:
			#newBedTmp=newBed
			#newBed=dict()	
			newChromDict=dict()
			origChromDict=newBed[bin1Chr]
			newBed[bin1Chr]=newChromDict
			
			for bed1coord,bed1coordpieces in bed1entrydict.items():
				more1=bed1ChromDict[bed1coord]
				bed1coordpieces=list(bed1coordpieces)				
				if len(bed1coordpieces)==1:
					#add directly
					newChromDict[bed1coordpieces[0]]=more1
				else:
					#may need collapsing
					overlapgraph=dict()
					visited=dict()
					updateOverlapGraph(overlapgraph,visited,bed1coordpieces)
					regions=overlapGraph2MergedRegions(overlapgraph,visited,bed1coordpieces)
					for newMergedBound,setOfOrigBounds in regions:
						#=region
						newChromDict[tuple(newMergedBound)]=more1
	

	if mergeBed1All:
		newBedTmp=newBed
		binTmp=binIntv(newBedTmp,mb1allbinIntv)
		print >> stderr,""
		print >> stderr,"merge bed 1 all",
		newBed=mergeIntervals(binTmp,newBedTmp)
		
			
	return newBed


def toStrArray(L):
	oL=[]
	for s in L:
		oL.append(str(s))
	return oL

def printBed(stream,bed):
	for bedchrom,chromdict in bed.items():
		for coord,more in chromdict.items():
			if len(more)==0:
				print >> stream,"\t".join(toStrArray((bedchrom,)+coord))
			else:
				for m in more:
					print >> stream,"\t".join(toStrArray((bedchrom,)+coord+m))


def printUsageAndExit(programName):
	print >> stderr,programName,"[Options] bedfile1 bedfile2"
	print >> stderr,"Options:"
	print >> stderr,"--min-overlap length [1] set the minimal overlap length"
	print >> stderr,"--add-chrom-if-needed   if one of the file doesn't have chr prefix but the other has, then add in the chr in the matching stage such that these can be matched"
	print >> stderr,"--bin-interval interval [100000] set the interval for binning. Binning is used to accelerate overlaps"
	print >> stderr,"--warn-duplicates turn on warnings for duplicate entries"
	print >> stderr,"--remove-duplicates remove duplicate entries"
	print >> stderr,"--merge-per-bed1 merge pieces of intervals from the same bedfile1 entry into one (as in Galaxy). Output only fields that is in bedfile1"
	print >> stderr,"--merge-bed1-all merge pieces of intervals from the whole bed1file entry into one. Output only coordinates"
	exit()

def testMergeIntervals():
	chromdict=dict()
	bed=dict()
	bed["try"]=chromdict

	chromdict[(0,50)]=['a']
	chromdict[(39,65)]=['b']
	chromdict[(62,89)]=['c']
	chromdict[(92,125)]=['d']
	bin=binIntv(bed,20)

	mergeIntervals(bin,bed)
	exit()
'''
overlapG {(62, 89): set([(39, 65)]), (0, 50): set([(39, 65)]), (39, 65): set([(62, 89), (0, 50)])}
visited {(62, 89): False, (0, 50): False, (39, 65): False}
regions [[[92, 125], set([(92, 125)])], [[0, 89], set([(62, 89), (0, 50), (39, 65)])]]
'''

def main():
	

	programName=argv[0]
	opts,args=getopt(argv[1:],'',['warn-duplicates','remove-duplicates','min-overlap=','add-chrom-if-needed','merge-per-bed1','merge-bed1-all','bin-interval='])
	try:
		bedfile1,bedfile2=args
	except:
		printUsageAndExit(programName)

	binInterval=100000
	warnduplicate=False
	appenduplicate=True
	mergeBed1All=False
	overlapLength=1
	
	addChromIfNeeded=False
	collapsePerBed1=False

	for o,v in opts:
		if o=='--min-overlap':
			overlapLength=int(v)
		elif o=='--add-chrom-if-needed':
			addChromIfNeeded=True
		elif o=='--warn-duplicates':
			warnduplicate=True
		elif o=='--remove-duplicates':
			appenduplicate=False
		elif o=='--bin-interval':
			binInterval=int(v)
		elif o=='--merge-per-bed1':
			collapsePerBed1=True
		elif o=='--merge-bed1-all':
			mergeBed1All=True

	print >> stderr,"reading in",bedfile1
	bed1=readBed(bedfile1,appenduplicate,warnduplicate)
	print >> stderr,"reading in",bedfile2
	bed2=readBed(bedfile2,appenduplicate,warnduplicate)
	print >> stderr,"making bins"
	bin1=binIntv(bed1,binInterval)
	#print >> stderr,bin1
	bin2=binIntv(bed2,binInterval)
	#print >> stderr,bin2
	print >> stderr,"overlap...",
	obed=overlapPiecesOfIntervalsByBins(bin1,bin2,bed1,bed2,appenduplicate,warnduplicate,overlapLength,addChromIfNeeded,collapsePerBed1,mergeBed1All,binInterval)
	#obed=overlapPiecesOfIntervals(bed1,bed2)
	print >> stderr,"... done."
	print >> stderr,"printing"
	printBed(stdout,obed)

if __name__=='__main__':
	main()	
	
