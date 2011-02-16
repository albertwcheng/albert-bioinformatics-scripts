#!/usr/bin/python

#######
#
#  ErrModelCluster2TreeHMClusterFile.py version 1.0 <20091209>
#  Albert W. Cheng
#  awcheng@mit.edu
#  
#  Please redistribute or modify if needed, but remember to put your modification log here  
# 
#  This script takes young lab error model outputs and produce a bin-wise cluster file for cluster3 or pyClusterArray.py to generate cluster heatmap or array correlation heatmap
#
#######



import sys
from sys import stdout,stderr
from getopt import *

#cmd files files files

#bash-3.2$ colStat.py CLUSTER_START_liverIPS_k4me3_mm8_TSS_091105_194437 
#[:::::			R 1			:::::]
#Index			Excel			Field
#-----			-----			-----
#1			A			GENEID
#2			B			NAME
#3			C			-4000_liverIPS_k4me3_mm8_TSS
#4			D			-3900_liverIPS_k4me3_mm8_TSS
#82			CD			3900_liverIPS_k4me3_mm8_TSS

def compare2ndElement(x,y):
	xv=x[1]
	yv=y[1]
	if xv>yv:
		return 1
	elif xv==yv:
		return 0
	else: #xv<yv
		return -1

def Mi2MInPlace(Mi,M):
	for (MiRow,MRow) in zip(Mi,M):
		for i,val in MiRow:
			MRow[i]=val
	
def M2Mi(M):
	Mi=[]
	for row in M:
		newMiRow=[]
		Mi.append(newMiRow)
		for i in range(0,len(row)):
			newMiRow.append([i,row[i]])
	
	return Mi


def fillNormalizer(Mi,normalizer,method):

	numsamples=len(Mi)
	numvalues=len(Mi[0])
	
	methods={"min":-1,"mean":0,"max":1,"sum":2,"rank":3}
	
	try:
		method=methods[method.lower()]
	except KeyError:
		print >> stderr,"undefined method for normalizer:",method
		exit()
	
	for i in range(0,numvalues):
		SUM=0.0
		MINV=""
		MAXV=""
		
		for j in range(0,numsamples):
			Miji=Mi[j][i][1]
			
			SUM+=Miji
			if MINV=="":
				MINV=Miji
			else:
				MINV=min(MINV,Miji)
				
			if MAXV=="":
				MAXV=Miji
			else:
				MAXV=max(MAXV,Miji)
	
		if method==-1:
			normalizer.append(MINV)
		elif method==0:
			normalizer.append(SUM/numsamples)
		elif method==1:
			normalizer.append(MAXV)
		elif method==2:
			normalizer.append(SUM)
		elif method==3:
			normalizer.append(i+1)

def printM(stream,M):
	if len(M)<1:
		return
		
	numsamples=len(M)
	numvalues=len(M[0])
	
	for i in range(0,numvalues):
		print >> stream,str(M[0][i]),
		for j in range(1,numsamples):
			print >> stream,"\t"+str(M[j][i]),
			
		print >> stream,""
		
	print >> stream,""


	
def quantileNormalizeMInPlace(M,method):
#	print >>stderr,"M before normalization"
#	printM(stderr,M)

	Mi=M2Mi(M)
	
#	print >> stderr,"Mi beforeSort"
#	printM(stderr,Mi)
	
	quantileNormalizeMiInPlace(Mi,method)
	
#	print >> stderr,"Mi afterQuantile"
#	printM(stderr,Mi)	
	
	Mi2MInPlace(Mi,M)
	
#	print >>stderr,"M after normalization"
#	printM(stderr,M)	
	
def quantileNormalizeMiInPlace(Mi,method):
	if len(Mi)<2:
		return
		
	numvalues=len(Mi[0])
	
	normalizer=[]
		
	#now sort by quantile
	for MiRow in Mi:
		MiRow.sort(compare2ndElement)
	
#	print >> stderr,"Mi afterSort"
#	printM(stderr,Mi)
	
	#now normalize
	fillNormalizer(Mi,normalizer,method)
	
#	print >> stderr,"normalizer"
#	printM(stderr,[normalizer])
	
	#now redistribute values
	for MiRow in Mi:
		for i in range(0,numvalues):
			MiRow[i][1]=normalizer[i]
	

def writeNewClusterFile(stream,D,COORD,SAMPLES,fill):
	#fil=open(DstFilename,'w')
	
	#first row
	#print >> sys.stderr, SAMPLES
	toPrint=["GENEID"]+SAMPLES
	print >> stream,"\t".join(toPrint)
	
	for GeneName,geneRecord in D.items():
		if not fill:
			failedGene=False
			for coordValues in geneRecord:
				if len(coordValues)==0:
					failedGene=True
			if failedGene:
				continue
			
		for j in range(0,len(COORD)):
			coord=COORD[j]
			toPrint=[GeneName+"_"+coord]
			for i in range(0,len(SAMPLES)):
				try:
					toPrint.append(geneRecord[i][j])
				except IndexError:
					if fill:
						toPrint.append("0")				
			try:		
				print >> stream,"\t".join(toPrint)
			except TypeError:
				print >> stderr,toPrint
				sys.exit()
	
	
	
	#fil.close()



def sumOf(L):
	sum=0.0
	for x in L:
		sum+=x
	
	return sum


def floatList(strL):
	fL=[]
	for x in strL:
		fL.append(float(x))
	
	return fL

def makeCollapsedCluster(D,COORD,SAMPLES,method): #output new [Dp,COORDp]
	methods={"min":-1,"mean":0,"max":1,"sum":2}
	COORDp=[method]
	try:
		method=methods[method]
	except KeyError:
		print >> stderr,"unknown method:",method
		exit()
		
	
	Dp=dict()
	
	#print >> sys.stderr, D
	
	for GeneName,geneRecord in D.items():
		sampleData=[]
		Dp[GeneName]=sampleData
		for i in range(0,len(SAMPLES)):
			coordData=floatList(geneRecord[i])
			if len(coordData)==0:
				if method in [-1,0,1,2]:
					sampleData.append(["0.0"])
			else:
				if method==-1:
					sampleData.append([str(min(coordData))])
				elif method==0:
					sampleData.append([str(sumOf(coordData)/len(coordData))])
				elif method==1:
					sampleData.append([str(max(coordData))])
				elif method==2:
					sampleData.append([str(sumOf(coordData))])
			
						

		
	
	return [Dp,COORDp]

def addClusterFile(filename,D,COORD,SAMPLES,fileIndx,numFile,fill):
	fil=open(filename)
	lino=0
	#coord=[]
	
	nCoord=len(COORD)
	
	baseFile=(fileIndx==0)
	
	for lin in fil:
		lino+=1
		lin=lin.strip("\r\n")
		fields=lin.split("\t")
		
		
		if ( not baseFile ) and len(fields)!=nCoord+2:
			print >> sys.stderr,"number of samples not matched, need",nCoord,"got",len(fields)-2
			sys.exit()
		
		if lino ==1:
			#read header
			if baseFile:
				
				for i in range(2,len(fields)):
					field=fields[i]
					sampleNameSplit=field.split("_")
					COORD.append(sampleNameSplit[0])
					if i==2:
						sampleName="_".join(sampleNameSplit[1:])
						SAMPLES.append(sampleName)
						
						#print >> sys.stderr,sampleNameSplit
			else:
				#not base File
				for i,coord in zip(range(2,len(fields)),COORD):
					field=fields[i]
					sampleNameSplit=field.split("_")
					thisCoord=sampleNameSplit[0]
					if thisCoord!=coord:
						print >> sys.stderr,"unmatched position in file",filename,"coord",thisCoord,"vs",coord
						sys.exit()
					if i==2:
						sampleName="_".join(sampleNameSplit[1:])
						SAMPLES.append(sampleName)
					
		else:
			thisGeneID=fields[0]
			if baseFile:
				if D.has_key(thisGeneID):
					print >> sys.stderr,"Error: duplicate Gene ID",thisGeneID
					sys.exit()
				
				geneRecord=[]
				D[thisGeneID]=geneRecord
				for i in range(0,numFiles):
					geneRecord.append([])
			
			else:
				try:
					geneRecord=D[thisGeneID]
				except KeyError:
					if not fill:
						#print >> sys.stderr,"Error: unmatched Gene ID",thisGeneID,"ignored"
						continue
					else:
						geneRecord=[]
						D[thisGeneID]=geneRecord
						for i in range(0,numFiles):
							geneRecord.append([])
					
			
			#now get geneSampleRecord
			geneRecord[fileIndx]=fields[2:]
			#print >> sys.stderr, geneRecord[fileIndx]
			
				
			
				
				
		
			

		
		
	fil.close()

def prepareInputForQuantileNormalizationFromCollapsedData(Dp,SAMPLES):
	M=[]
	GeneNames=[]
	
	for sample in SAMPLES:
		sampleVector=[]
		M.append(sampleVector)
	

	for GeneName,geneRecord in Dp.items():
		GeneNames.append(GeneName)
		for i in range(0,len(SAMPLES)):
			M[i].append(float(geneRecord[i][0]))
	
	return [GeneNames,M]

def updateCollapsedDataFromNormalizedMatrixInPlace(Dp,GeneNames,M): #return scaling factor matrix
	
	lambdaMatrix=[]
	
	for i in range(0,len(M)):
		lambdaMatrix.append([])
	
	
	
	
	for r in range(0,len(GeneNames)):
		GeneName=GeneNames[r]
		geneRecord=Dp[GeneName]
		for i in range(0,len(M)):
			prevValue=float(geneRecord[i][0])
			newValue=M[i][r]
			geneRecord[i]=[str(M[i][r])]
			try:
				lambdaMatrix[i].append(float(newValue)/prevValue)
			except ZeroDivisionError:
				lambdaMatrix[i].append(float(newValue))
				
	return lambdaMatrix
	
def dup(x,times):
	L=[]
	for i in range(0,times):
		L.append(x)
	
	return L

def rescaleInStr(L,lamb):
	for i in range(0,len(L)):
		L[i]=str(float(L[i])*lamb)
			
def rescaleClusterFileInPlace(D,COORD,GeneNames,lambdaMatrix):
	
	coordLength=len(COORD)
	
	for r in range(0,len(GeneNames)):
		GeneName=GeneNames[r]
		geneRecord=D[GeneName]
		for i in range(0,len(geneRecord)):
			lamb=lambdaMatrix[i][r]
			if len(geneRecord[i])==0:
				geneRecord[i]=dup(str(lamb),coordLength)
			else:
				rescaleInStr(geneRecord[i],lamb)
				
				

def printUsageAndExit():
	print >> sys.stderr,"Usage:",programName,"file1 file2 .... fileN > un-normalized-file"
	print >> sys.stderr,"e.g., python ErrModelCluster2TreeHMClusterFile.py -q mean -c collapsedfile.out -n collapsednfile.out -r max -s qnorm.cluster CLUST* > notnorm.cluster"
	print >> sys.stderr,"collapsedfile.out will be the collapsed (by taking max/peak) peak file (not normalized). collapsednfile will be the collapsed quantile-normalized (taking mean of each quantile) peak file. qnorm.cluster is the rescaled bin-values rescaled based on quantile-normalized peak values. notnorm.cluster is the non-normalized bin-values"
	#print >> sys.stderr,"-o,--overlap only overlapped genes"
	print >> sys.stderr,"-q,--quantile-normalize method quantile normalize collapsed region by [min,mean,max,sum,rank]"
	print >> sys.stderr,"-c,--output-collapsed-file filename whether to output collapsed file and the filename"
	print >> sys.stderr,"-n,--output-collapsed-normalized-file filename whether to output collapsed and normalized peak file and the filename"	
	print >> sys.stderr,"-r,--collapse-region method collapse promoter regions by [min,mean,max,sum]"
	print >> sys.stderr,"-s,--output-qnorm-rescaled-cluster-file filename whether to output quantile-normalization-rescaled cluster file and the filename"

	sys.exit()	
	
if __name__=="__main__":
	
	programName=sys.argv[0]
	opts,args=getopt(sys.argv[1:],"q:c:r:n:s:",["quantile-normalize=","output-collapsed-file=","collapse-region","--output-collapsed-normalized-file","output-qnorm-rescaled-cluster-file"])

	#o overlap
	#the overlap option is disabled.
	
	fill=True
	quantileNormalize=[False,""]
	outputCollapsedFile=[False,""]
	collapseRegionBy=[False,""]
	outputCollapsedNormalizedFile=[False,""]
	outputQNormRescaledClusterFile=[False,""]
	
	for o,v in opts:
		if o in ['-o','--overlap']:
			fill=False
		elif o in ['-q','--quantile-normalize']:
			quantileNormalize=[True,v] #method
		elif o in ['-c','--output-collapsed-file']:
			outputCollapsedFile=[True,v] #filename
		elif o in ['-r','--collapse-region']:	
			collapseRegionBy=[True,v] #method
		elif o in ['-n','--output-collapsed-normalized-file']:
			outputCollapsedNormalizedFile=[True,v] #filename
		elif o in ['-s','--output-qnorm-rescaled-cluster-file']:
			outputQNormRescaledClusterFile=[True,v] #filename
			
	if (outputCollapsedFile[0] or quantileNormalize[0]) and not collapseRegionBy[0]:
		print >> sys.stderr,"please specify --collapse-region flag"
		printUsageAndExit()
		
	
	if len(args)<1:
		printUsageAndExit()
	
	D=dict()
	COORD=[]
	SAMPLES=[]
	
	files=args
	numFiles=len(files)
	for fileIdx in range(0,numFiles):
		print >> sys.stderr,"processing",fileIdx+1,"/",numFiles,":",files[fileIdx]
		addClusterFile(files[fileIdx],D,COORD,SAMPLES,fileIdx,numFiles,fill)
	
	collapseRegionByFlag,collapseRegionByMethod=collapseRegionBy
	quantileNormalizeFlag,quantileNormalizeMethod=quantileNormalize
	outputCollapsedFileFlag,outputCollapsedFilename=outputCollapsedFile
	outputCollapsedNormalizedFileFlag,outputCollapsedNormalizedFilename=outputCollapsedNormalizedFile
	outputQNormRescaledClusterFileFlag,outputQNormRescaledClusterFilename=outputQNormRescaledClusterFile
	
	writeNewClusterFile(stdout,D,COORD,SAMPLES,fill)
	
	if collapseRegionByFlag:
		[Dp,COORDp]=makeCollapsedCluster(D,COORD,SAMPLES,collapseRegionByMethod)
	
	if outputCollapsedFileFlag:
		fil=open(outputCollapsedFilename,'w')
		writeNewClusterFile(fil,Dp,COORDp,SAMPLES,fill)
		fil.close()
		
	if quantileNormalizeFlag:
		#print >> stderr,Dp
		[GeneNames,M]=prepareInputForQuantileNormalizationFromCollapsedData(Dp,SAMPLES)
		quantileNormalizeMInPlace(M,quantileNormalizeMethod)
		lambdaMatrix=updateCollapsedDataFromNormalizedMatrixInPlace(Dp,GeneNames,M)
	
	if outputCollapsedNormalizedFileFlag:
		fil=open(outputCollapsedNormalizedFilename,'w')
		writeNewClusterFile(fil,Dp,COORDp,SAMPLES,fill)
		fil.close()		
		
	if outputQNormRescaledClusterFileFlag:
		rescaleClusterFileInPlace(D,COORD,GeneNames,lambdaMatrix)
		fil=open(outputQNormRescaledClusterFilename,'w')
		writeNewClusterFile(fil,D,COORD,SAMPLES,fill)
		fil.close()				
		
	
		
