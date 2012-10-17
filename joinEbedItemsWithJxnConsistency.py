#!/usr/bin/env python

from joinBedByOverlap import *
from sys import *


#interval1=(start0,end1)
#interval2=(start0,end1)
def intervalOverlap(interval1,interval2):
	return min(interval1[1],interval2[1])-max(interval1[0],interval2[0])

def doesIntervalsOverlap(interval1,interval2):
	return intervalOverlap(interval1,interval2)>0

def leftContainedInRight(left,right):
	return left[0]>=right[0] and left[1]<=right[1]

#bedblocks=[(gstart0,gend1),(start0,gend1),...]
def doesEbedsHaveConsistentJxn(bed1blocks,bed2blocks,bed2ContainedInBed1=False):
	numBed1Blocks=len(bed1blocks)
	numBed2Blocks=len(bed2blocks)
	if numBed1Blocks==1 and numBed2Blocks==1:
		if bed2ContainedInBed1:
			return bed1blocks[0][0]<=bed2blocks[0][0] and bed1blocks[0][1]>=bed2blocks[0][1]
		else:
			return doesIntervalsOverlap(bed1blocks[0],bed2blocks[0])

	i=0
	j=0
	
	
	while not doesIntervalsOverlap(bed1blocks[i],bed2blocks[j]):

		while i<numBed1Blocks and bed1blocks[i][1] <= bed2blocks[j][0]:
			i+=1
			#print >> stderr,"i->",i
			
		if i==numBed1Blocks or j==numBed2Blocks:
			#print "bound reached before finding LMM, i=%d j=%d" %(i,j)
			return False			
			
		while j<numBed2Blocks and bed2blocks[j][1] <= bed1blocks[i][0]:
			j+=1
			#print >> stderr,"j->",j
		
		if i==numBed1Blocks or j==numBed2Blocks:
			#print "bound reached before finding LMM, i=%d j=%d" %(i,j)
			return False
			
		#print >> stderr, "i,j=",i,j
	
	bed1LMM=i
	bed2LMM=j
	
	#print >> stderr, "bed1LMM=%d bed2LMM=%d" %(bed1LMM, bed2LMM)
	
	

	
	
	if bed1LMM>0:
		if bed2LMM>0:
			return False
		#bed2LMM==0:
		if bed2blocks[bed2LMM][0] < bed1blocks[bed1LMM][0]:
			return False
	else: #bed1LMM==0
		if bed2LMM>0:
			if bed1blocks[bed1LMM][0] < bed2blocks[bed2LMM][0]:
				return False

	#i=bed1LMM+1
	#j=bed2LMM+1
	
	while i<numBed1Blocks-1 and j<numBed2Blocks-1:
		if bed1blocks[i][1]!=bed2blocks[j][1]:
			return False
		if bed1blocks[i+1][0]!=bed2blocks[j+1][0]:
			return False
		
		#if i<numBed1Blocks-2 and j<numBed2Blocks-2:
		#	if bed1blocks[i][1]!=bed2blocks[j][1]:
		#		return False	
			
	
		i+=1
		j+=1
	
	
	#print "pass"
	
	if i==numBed1Blocks-1:
		if j<numBed2Blocks-1:
			if bed1blocks[i][1]>bed2blocks[j][1]:
				return False
	else: #i<|bed1blocks|-1 and j==|bed2blocks|-1 becoz it has to end the while loop above
		if bed2blocks[j][1] > bed1blocks[i][1]:
			return False
	
	if bed2ContainedInBed1:
		condSatStart=False
		condSatEnd=False
		for bed1block in bed1blocks:
			if bed2blocks[0][0]>=bed1block[0] and bed2blocks[0][0]<bed1block[1]:
				condSatStart=True
			if bed2blocks[-1][1]>bed1block[0] and bed2blocks[-1][1]<=bed1block[1]:
				condSatEnd=True
				
		if not condSatStart or not condSatEnd:
			return False
			
	return True


def getFieldWithDefaultValue(fields,idx,defaultValue):
	try:
		#print >> stderr,"reading fields",idx
		return fields[idx]
	except:
		return defaultValue

def readEBedInPlace(bedExons,filename):
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
		
		if len(lin)==0 or lin[0]=='#' or lin[0:5]=='track':
			continue
		
		try:
			
			chrom,chromStartG0,chromEndG1=fields[0:3]
			chromStartG0=int(chromStartG0)
			chromEndG1=int(chromEndG1)			
			name=getFieldWithDefaultValue(fields,3,"")
			score=getFieldWithDefaultValue(fields,4,"")
			strand=getFieldWithDefaultValue(fields,5,".")
			thickStartG0=int(getFieldWithDefaultValue(fields,6,str(chromStartG0)))
			thickEndG1=int(getFieldWithDefaultValue(fields,7,str(chromEndG1)))
			itemRGB=getFieldWithDefaultValue(fields,8,"0,0,0")
			blockCount=int(getFieldWithDefaultValue(fields,9,"1"))
			blockSizes=getFieldWithDefaultValue(fields,10,str(chromEndG1-chromStartG0))
			#,name,score,strand,thickStartG0,thickEndG1,itemRGB,blockCount,blockSizes,blockStarts0=fields
			blockStarts0=getFieldWithDefaultValue(fields,11,"0")

			if strand not in ["+","-"]:
				#correct!
				strand="."
			
			blockSizeSplits=blockSizes.split(",")
			blockSizes=[]
			for s in blockSizeSplits:
				s=s.strip()
				if len(s)>0:
					blockSizes.append(int(s))
			blockStarts0Splits=blockStarts0.split(",")
			blockStarts0=[]
			for s in blockStarts0Splits:
				s=s.strip()
				if len(s)>0:
					blockStarts0.append(int(s))		
				
			if len(blockStarts0)!=blockCount or len(blockSizes)!=blockCount:
				print >> stderr,"block count not consistent with blockStarts or blockSizes data"
				raise ValueError
		except:
			print >> stderr,"format error",fields
			raise ValueError
	
		try:
			chromBed=bedExons[chrom]
		except:
			chromBed=dict()
			bedExons[chrom]=chromBed

	
		exonGBlocks=[]
	
		for bStart0,bSize in zip(blockStarts0,blockSizes):
			exonGBlocks.append((bStart0+chromStartG0,bStart0+chromStartG0+bSize))

		exonGBlocks=tuple(exonGBlocks)
		
		coordKey=(chromStartG0,chromEndG1)
		try:
			bedstruct=chromBed[coordKey]
		except:
			bedstruct=[]
			chromBed[coordKey]=bedstruct
			
		bedstruct.append((name,exonGBlocks,lin))
					

	fil.close()
	return bedExons



def testCase():
	ebed1=[(0,5)]
	ebed2=[(3,7)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2,True)


	ebed1=[(0,5)]
	ebed2=[(3,5)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2,True)
	
	ebed1=[(0,5),(10,15)]
	ebed2=[(3,5)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)
	
	ebed1=[(0,5),(10,15)]
	ebed2=[(3,7)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)

	ebed1=[(0,5),(10,15)]
	ebed2=[(3,5),(11,12)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)

	ebed1=[(0,5),(10,15)]
	ebed2=[(3,5),(10,12)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)
	
	ebed1=[(0,1),(2,5),(10,15)]
	ebed2=[(3,5),(10,12)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)	

	ebed1=[(0,1),(2,5),(10,15)]
	ebed2=[(-1,-3),(3,5),(10,12)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)	
	
	ebed1=[(0,1),(2,5),(10,15)]
	ebed2=[(22,29),(33,36)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)		
	
	ebed1=[(3,5),(10,12)]
	ebed2=[(0,1),(2,5),(10,15)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)	
	
	ebed1=[(3,5),(10,12),(14,16)]
	ebed2=[(0,1),(2,5),(10,15)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)	
	
	ebed1=[(3,5),(10,12),(14,16)]
	ebed2=[(0,1),(2,5),(10,11)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)		


	ebed1=[(3,5),(10,12),(14,16)]
	ebed2=[(0,1),(2,5),(10,11)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2,True)	

	ebed1=[(0,1),(2,5),(10,11)]
	ebed2=[(3,5),(10,12),(14,16)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)	
	
	
	ebed1=[(0,1),(2,5),(10,12),(18,19)]
	ebed2=[(3,5),(10,12),(14,16)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)		
	
	
	ebed1=[(0,1),(2,5),(10,12),(15,16)]
	ebed2=[(3,5),(10,12),(14,16)]
	print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)					
	exit(1)

if __name__=='__main__':


	#ebed1=[(0, 3), (5, 10), (12, 14), (16, 20)]
	#ebed2=[(4, 5)]
	#print ebed1,ebed2,"\n",doesEbedsHaveConsistentJxn(ebed1,ebed2)
	#testCase()
	#

	from optparse import OptionParser
	
	usage="usage: %prog  [options] file1 file2  > ofilename"
	parser=OptionParser(usage)

	clusterNumber=0

	parser.add_option("--bin-interval",dest="binInterval",default=100000,type="int",help="set binning interval for accelarating overlap calculation [100000]")
	parser.add_option("--overlap-lower-bound",dest="overlapLength",default=1,type="int",help="set the lower bound for overlap in bases [1]")
	parser.add_option("--bed2-contained-in-bed1",dest="bed2Contained",default=False,action="store_true",help="requiring the bed2 item to be contained in bed1, i.e., no protrusion at ends")
	try:
		(options,args)=parser.parse_args()
		filename1,filename2=args
	except:
		parser.print_help()
		exit(0)

	addChromIfNeeded=True
	appenduplicate=False
	warnduplicate=False

	bedExons1=dict()
	bedExons2=dict()

	readEBedInPlace(bedExons1,filename1)
	bedExonBins1=binIntv(bedExons1,options.binInterval)
	
	readEBedInPlace(bedExons2,filename2)
	bedExonBins2=binIntv(bedExons2,options.binInterval)
	
	jBedExons=joinIntervalsByBins(bedExonBins1,bedExonBins2,bedExons1,bedExons2,options.overlapLength,addChromIfNeeded,appenduplicate,warnduplicate,"","")

	print >> stderr,""
	#jbed[(bin1Chr,coord1[0],coord1[1],coord2[0],coord2[1])]=(tuple(name,tuple(gblocks)),tuple(tuple(name,tuple(gblocks))),ob)
	
	for key,v in jBedExons.items():
		#print >> stderr, v
		for bed1Entries,bed2Entries,ob in v:
			#print >> stderr,"bed1Entries",bed1Entries,"bed2Entries",bed2Entries
			for i in range(0,len(bed1Entries)):
				for j in range(0,len(bed2Entries)):
					#print >> stderr,"bed1Entries[i]",bed1Entries[i],"bed2Entries[j]",bed2Entries[j]
					
						
				
					name1,gblocks1,lin1=bed1Entries[i]
					name2,gblocks2,lin2=bed2Entries[j]
					
					#print >> stderr,"gblocks1",gblocks1
					#print >> stderr,"gblocks2",gblocks2
					if doesEbedsHaveConsistentJxn(gblocks1,gblocks2,options.bed2Contained):
						print lin1+"\t"+lin2

	exit(1)

