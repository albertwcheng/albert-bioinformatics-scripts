#!/usr/bin/env python

'''

Join Bed File rows if they are overlapped. Requires simpleBedOverlap.py

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

easyClusterGenesOnEbed.py --not-append-filename-to-combined-name --transcript-exon-number-lower-bound 0 --splice-site-align-lower-bound 1 --strand-aware --use-friendly-name ACMmuRNA 8 friendlymap.txt --randomize-color --add-header MmuGenes "MmnGenes Track" itemRgb/On+visibility/full tryEbedToCluster.bed  > clusteredTry.bed 

easyClusterGenesOnEbed.py --not-append-filename-to-combined-name --transcript-exon-number-lower-bound 0 --splice-site-align-lower-bound 1 --use-friendly-name ACMmuRNA 8 friendlymap.txt --randomize-color --add-header MmuGenes "MmnGenes Track" itemRgb/On+visibility/full Mmu.ESC.ebed acembly.ebed  > MmuESCAceView.ebed 


easyClusterGenesOnEbed.py --not-append-filename-to-combined-name --transcript-exon-number-lower-bound 0 --splice-site-align-lower-bound 1 --use-friendly-name ACMmuRNA 8 friendlymap.chr10.txt --randomize-color --add-header MmuGenes "MmnGenes Track" itemRgb/On+visibility/full Mmu.ESC.chr10.ebed acembly.chr10.ebed  > MmuESCAceView.chr10.ebed 

easyClusterGenesOnEbed.py --not-append-filename-to-combined-name --transcript-exon-number-lower-bound 0 --splice-site-align-lower-bound 1 --use-friendly-name ACMmuRNA 8 friendlymap.supergenius.txt --randomize-color --add-header MmuGenes "MmnGenes Track" itemRgb/On+visibility/full Mmu.ESC.ebed acembly.ebed  > MmuESCAceView.supergenius.ebed 


'''

from joinBedByOverlap import *
from sys import *
from random import randint



'''
extended bed (ebed)

1) chrom
2) chrom start g0
3) chrom end g1
4) name
5) score
6) strand
7) thickStart = CDS Start g0
8) thickEnd = CDS End g1
9) itemRGB
10) blockCount = exonCount
11) blockSizes (,)
12) blockStarts (,) relative to Chom Start in 0-based

----

'''

'''
returns
	bedExons[chrom][(exonstart,exonend)]=[transcriptstruct]
		
	transcriptstruct=(chrom,chromStartG0,chromEndG1,name,score,strand,thickStart0,thickEndG1,itemRGB,blockCount,exonStartsG0,exonEndsG1)
	exonStartsG=tuple(starts,...)
	exonEndsG1=tuple(ends,...)
'''

def findGroupFrom(SimilarityGraph,GroupMap,GroupName,SourceName):
	#visit the source first
	InGroup=[SourceName]
	
	GroupMap[SourceName]=GroupName
	
	#now queue
	Q=[]
	Q.extend(SimilarityGraph[SourceName])
	while len(Q)>0:
		u=Q.pop(0)
		
				
		if GroupMap[u]!="":
			if GroupMap[u]!=GroupName:
				print >> stderr,"error: this node was assigned previously to",GroupMap[u],"while attempting to reassign to",GroupName
				exit()
			
			#this has been assigned (so have been visited) so continue
			continue

		
		GroupMap[u]=GroupName
		InGroup.append(u)
		#now add in all neighbors!
		
		vs=SimilarityGraph[u]

		
		#add to queue
		Q.extend(vs)
	
	return InGroup

def findGroups(SimilarityGraph):
	Names=SimilarityGraph.keys()
	#initialize motifGroupMap
	GroupMap=dict()
	Groups=dict()
	for Name in Names:
		GroupMap[Name]=""
	
	I=0
	
	for Name in Names:
		if GroupMap[Name]=="":
			I+=1
			GroupName="Group"+str(I)
			InGroup=findGroupFrom(SimilarityGraph,GroupMap,GroupName,Name)
			Groups[GroupName]=InGroup
	
	return (Groups,GroupMap)

def findGroupFromWithReevaluator(SimilarityGraph,GroupMap,GroupName,SourceName,reevaluator,extData):
	#visit the source first
	InGroup=[SourceName]
	
	GroupMap[SourceName]=GroupName
	
	#now queue
	Q=[]
	for t in SimilarityGraph[SourceName]:
		if reevaluator(SourceName,t,extData):
			Q.append(t)

	while len(Q)>0:
		u=Q.pop(0)
		
				
		if GroupMap[u]!="":
			if GroupMap[u]!=GroupName:
				print >> stderr,"error: this node was assigned previously to",GroupMap[u],"while attempting to reassign to",GroupName
				exit()
			
			#this has been assigned (so have been visited) so continue
			continue

		
		GroupMap[u]=GroupName
		InGroup.append(u)
		#now add in all neighbors!
		
		vs=SimilarityGraph[u]

		
		#add to queue
		#Q.extend(vs)
		for t in vs:
			if reevaluator(u,t,extData):
				Q.append(t)
	
	return InGroup

def findGroupsWithReevaluator(SimilarityGraph,reevaluator,extData):
	Names=SimilarityGraph.keys()
	#initialize motifGroupMap
	GroupMap=dict()
	Groups=dict()
	for Name in Names:
		GroupMap[Name]=""
	
	I=0
	
	for Name in Names:
		if GroupMap[Name]=="":
			I+=1
			GroupName="Group"+str(I)
			InGroup=findGroupFromWithReevaluator(SimilarityGraph,GroupMap,GroupName,Name,reevaluator,extData)
			Groups[GroupName]=InGroup
	
	return (Groups,GroupMap)


def strandReevaluator(transcriptName1,transcriptName2,transcriptMap):
	transcriptStruct1=transcriptMap[transcriptName1]
	transcriptStruct2=transcriptMap[transcriptName2]
	strand1=transcriptStruct1[5]
	strand2=transcriptStruct2[5]
	#print >> stderr,"reeval",transcriptName1,transcriptName2,strand1,strand2
	return strand1==strand2

def coSpliceSiteReevaluator(transcriptName1,transcriptName2,extData):
	transcriptMap,threshold=extData
	transcriptStruct1=transcriptMap[transcriptName1]
	transcriptStruct2=transcriptMap[transcriptName2]
	XexonStartsG0=set(transcriptStruct1[10])
	XexonEndsG1=set(transcriptStruct1[11])
	YexonStartsG0=set(transcriptStruct2[10])
	YexonEndsG1=set(transcriptStruct2[11])

	exonStartsG0Common=XexonStartsG0 & YexonStartsG0
	exonEndsG1Common=XexonEndsG1 & YexonEndsG1
	#print >> stderr,"reeval",transcriptName1,transcriptName2,exonStartsG0Common,exonEndsG1Common
	return len(exonStartsG0Common)+len(exonEndsG1Common)>=threshold
	

def readEBedInPlace(bedExons,transcriptMap,filename,blockCountThreshold,appendFilenameToCombinedName):
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
		try:
			chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRGB,blockCount,blockSizes,blockStarts0=fields
			chromStartG0=int(chromStartG0)
			chromEndG1=int(chromEndG1)
			thickStartG0=int(thickStartG0)
			thickEndG1=int(thickEndG1)
			blockCount=int(blockCount)

			if strand not in ["+","-"]:
				#correct!
				strand="."
			
			if blockCount<blockCountThreshold:
				continue

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

		if appendFilenameToCombinedName:
			transcriptname=filename+"/"+name
		else:
			transcriptname=name

		if transcriptname in transcriptMap:
			print >> stderr,"duplicate name. abort",transcriptname
			exit()

		exonStartsG0=[]
		exonEndsG1=[]
	
		for bStart0,bSize in zip(blockStarts0,blockSizes):
			exonStartsG0.append(bStart0+chromStartG0)
			exonEndsG1.append(bStart0+chromStartG0+bSize)

		#exonStartsG0=tuple(exonStartsG0)
		#exonEndsG1=tuple(exonEndsG1)
			
		transcriptStruct=(chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRGB,blockCount,exonStartsG0,exonEndsG1,blockSizes,blockStarts0)		
		transcriptMap[transcriptname]=transcriptStruct

		for exonStartG0,exonEndG1 in zip(exonStartsG0,exonEndsG1):
			coordKey=(exonStartG0,exonEndG1)
			try:
				bedstruct=chromBed[coordKey]
			except:
				bedstruct=[]
				chromBed[coordKey]=bedstruct
			
			bedstruct.append(transcriptname)
					

	fil.close()
	return bedExons,transcriptMap

def sliceSubGraphByNodes(G,nodes):
	subGraph=dict()
	nodes=set(nodes)
	for u in nodes:
		subGraph[u]=G[u] & nodes

	return subGraph

def addDirectedEdgeToGraph(G,u,v):
	try:	
		AdjSet=G[u]
	except:
		AdjSet=set()
		G[u]=AdjSet

	AdjSet.add(v)

def getStrArray(L):
	Lp=[]
	for x in L:
		Lp.append(str(x))
	return Lp

def addUndirectedEdgeToGraph(G,u,v):
	addDirectedEdgeToGraph(G,u,v)
	addDirectedEdgeToGraph(G,v,u)

def fillPrefixUntil(S,length,filler):
	while len(S)<length:
		S=filler+S

	return S

if __name__=='__main__':
	from optparse import OptionParser
	
	usage="usage: %prog  [options] file1 file2 ... fileN > ofilename"
	parser=OptionParser(usage)

	clusterNumber=0

	parser.add_option("--strand-aware",dest="strandAware",default=False,action="store_true",help="strand information used")
	parser.add_option("--transcript-exon-number-lower-bound",dest="transcriptExonNumberThreshold",default=1,type="int",help="discard transcripts with less than this number of exons [1, i.e., discard single-exon transcripts]")
	#parser.add_option("--non-stiky",dest="nonSticky",default=False,action="store_true",help="non sticky. i.e., required clique in similarity graph")
	parser.add_option("--splice-site-align-lower-bound",dest="spliceSiteAlignThreshold",default=1,type="int",help="set the splice site alignment threshold [1]")
	parser.add_option("--bin-interval",dest="binInterval",default=100000,type="int",help="set binning interval for accelarating overlap calculation [100000]")
	parser.add_option("--overlap-lower-bound",dest="overlapLength",default=1,type="int",help="set the lower bound for overlap in bases [1]")
	parser.add_option("--use-friendly-name",dest="useFriendlyName",default=None,nargs=3,help="use friendly name <prefix>000001 for gene name. 3 args <prefix><forceNumberOfDigits><outputFile for writing the map of new name to original names>")
	parser.add_option("--attach-original-names",dest="attachOriginalNames",default=False,action="store_true",help="attach original names as an extra column")
	parser.add_option("--randomize-color",dest="randomizeColor",default=False,action="store_true",help="randomize color of items")
	parser.add_option("--add-header",dest="headerAttr",default=None,nargs=3,help="add header to the output bed file. <trackName> <description> <other args>. other_args=key/value+key/value. e.g., --add-header awesome awesomeTrackDescription itemRgb/On+visibility/full")
	parser.add_option("--not-append-filename-to-combined-name",dest="appendFilenameToCombinedName",default=True,action="store_false",help="do not attach filename to combined name")	
	addChromIfNeeded=True
	appenduplicate=False
	warnduplicate=False

	
	
	
	#parser.conversion=genePredFields2ebedFields
	try:
		(options,args)=parser.parse_args()
	except:
		parser.print_help()
		exit()
	

	filenames=args

	bedExons=dict()
	transcriptMap=dict()
	

	if len(filenames)<1:
		print >> stderr,"no files specified. Abort"
		parser.print_help()
		exit()


	if options.useFriendlyName!=None:
		options.useFriendlyName=list(options.useFriendlyName)
		options.useFriendlyName[1]=int(options.useFriendlyName[1])
		friendlyNameFout=open(options.useFriendlyName[2],"w")


	if options.headerAttr:
		print >> stdout,'track name="%s" description="%s"' %(options.headerAttr[0],options.headerAttr[1]),
		otherOpts=options.headerAttr[2].split("+")
		for o in otherOpts:
			key,value=o.split("/")
			print >> stdout,'%s="%s"' %(key,value),
		print >> stdout,""

	for filename in filenames:
		print >> stderr,"reading in bed",filename
		readEBedInPlace(bedExons,transcriptMap,filename,options.transcriptExonNumberThreshold,options.appendFilenameToCombinedName)
	
	print >> stderr,"done reading in beds"
	print >> stderr,"binning exons. binInterval=",options.binInterval
	bedExonBins=binIntv(bedExons,options.binInterval)
	print >> stderr,"done binning exons"

	jBedExons=joinIntervalsByBins(bedExonBins,bedExonBins,bedExons,bedExons,options.overlapLength,addChromIfNeeded,appenduplicate,warnduplicate,"","")
	print >> stderr,""
	#jbed[(bin1Chr,coord1[0],coord1[1],coord2[0],coord2[1])]=(tuple(bed1ChromDict[coord1]),tuple(bed2ChromDict[coord2]),ob)

	#now construct a graph
	'''
	Graph[nodeName]=set(nodeName)

	'''
	overlapGraph=dict()

	#preinitialize graph such that nothing is left out
	for transcriptName in transcriptMap.keys():
		overlapGraph[transcriptName]=set()

	for jbedKey,jbedValue in jBedExons.items():
		for infoStackX,infoStackY,ob in jbedValue:
			#avoid to itself.
			for transcriptNameX in infoStackX:
				for transcriptNameY in infoStackY:
					if transcriptNameX==transcriptNameY:
						continue

						#now connect them
					addUndirectedEdgeToGraph(overlapGraph,transcriptNameX,transcriptNameY)


	overlapGroups,Transcript2GroupMap=findGroups(overlapGraph)

	#now for each of the overlap group, do more sophisticated filtering

	

	for overlapGroupName,transcriptsInGroup in overlapGroups.items():
		#retraverse the graph on transcripts
		SubGraphs=[sliceSubGraphByNodes(overlapGraph,transcriptsInGroup)]

		if options.strandAware:
			newSubGraphs=[]
			for SubGraph in SubGraphs:
				newOverlapGroups,dummy=findGroupsWithReevaluator(SubGraph,strandReevaluator,transcriptMap)
				for dummy,newTranscriptsInGroup in newOverlapGroups.items():
					newSubGraphs.append(sliceSubGraphByNodes(SubGraph,newTranscriptsInGroup))
			
			SubGraphs=newSubGraphs ##replacement
		
		#findGroupsWithReevaluator(SubGraph,coSpliceSiteReevaluator,[transcriptMap,options.spliceSiteAlignThreshold])


		if options.spliceSiteAlignThreshold>=1:
			newSubGraphs=[]
			for SubGraph in SubGraphs:
				newOverlapGroups,dummy=findGroupsWithReevaluator(SubGraph,coSpliceSiteReevaluator,[transcriptMap,options.spliceSiteAlignThreshold])
				for dummy,newTranscriptsInGroup in newOverlapGroups.items():
					newSubGraphs.append(sliceSubGraphByNodes(SubGraph,newTranscriptsInGroup))
			
			SubGraphs=newSubGraphs ##replacement			

		#now we have a subgraph consisting of cluster of genes

		for SubGraph in SubGraphs:
			transcriptsInGroup=SubGraph.keys()			

			#now output this as a locus
			geneNames=[]
			for transcript in transcriptsInGroup:
				geneNames.append(transcript)
			
			geneNames.sort()

			clusterNumber+=1

			if options.randomizeColor:
				thisGeneColor=str(randint(0,255))+","+str(randint(0,255))+","+str(randint(0,255))

			geneNameCombined="|".join(geneNames)

			if options.useFriendlyName!=None:
				geneNumInfix=fillPrefixUntil(str(clusterNumber),options.useFriendlyName[1],"0")
				geneNameToShow=options.useFriendlyName[0]+geneNumInfix
				print >> friendlyNameFout,"%s\t%s" %(geneNameToShow,geneNameCombined)
			else:
				geneNameToShow=geneNameCombined
		
			#now write every transcript
			for idx in range(0,len(transcriptsInGroup)):
				chrom,chromStartG0,chromEndG1,name,score,strand,thickStart0,thickEndG1,itemRGB,blockCount,exonStartsG0,exonEndsG1,blockSizes,blockStarts0=transcriptMap[transcriptsInGroup[idx]]
				thisTranscriptName=geneNameToShow+"."+str(idx+1)
				if options.randomizeColor:
					itemRGB=thisGeneColor
				toPrint=[chrom,str(chromStartG0),str(chromEndG1),thisTranscriptName,str(score),strand,str(thickStart0),str(thickEndG1),itemRGB,str(blockCount),",".join(getStrArray(blockSizes)),",".join(getStrArray(blockStarts0))]
				if options.attachOriginalNames:
					toPrint.append(geneNameCombined)
				print >> stdout,"\t".join(toPrint)
				

	

	if options.useFriendlyName!=None:
		friendlyNameFout.close()	
