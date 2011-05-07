#!/usr/bin/env python

from sys import *
from getopt import getopt
from operator import itemgetter
from os.path import exists

complDict={'A':'T','a':'t','C':'G','c':'g','T':'A','t':'a','G':'C','g':'c','U':'A','u':'a'}	
	
	
def complementBase(c):
	global complDict
	try:
		return complDict[c]
	except:
		return c

def editDistance(s1,s2):
	if len(s1)!=len(s2):
		return 100000
	
	dist=0
	
	for i in range(0,len(s1)):
		x=s1[i]
		y=s2[i]
		if x.upper()!=y.upper():
			dist+=1

	return dist
	
#return None or the (barcodeMatched,ToFileString)
def findBestBarcodeMatchedEntry(barcodeListing,code,editDistanceMax,noTie=True):
	if editDistanceMax==0: #no mismatch allowed
		if not barcodeListing.has_key(code):
			return None
		else:
			return (code,barcodeListing[code])
	else:
		editDists=[]
		for codeEntry,codeToFile in barcodeListing.items():
			editDists.append((editDistance(code,codeEntry),codeEntry,codeToFile))
		
		#now sort edit Dist on first item
		editDists.sort(key=itemgetter(0))
		
		#now ascending
		#the first item is the best
		if noTie and editDists[1][0]==editDists[0][0]: #tie arising
			return None #tie assume no matched
		
		if editDists[0][0]>editDistanceMax:
			return None #not good match
		
		return (editDists[0][1],editDists[0][2]) #return the code matched and the toFile String
		
def reverse_complement(S):
	rc=""
	for i in range(len(S)-1,-1,-1):
		rc+=complementBase(S[i])
	
	return rc

'''
 @HWI-ST333_0096_FC:7:1101:1326:2106#CATGCC/1

 the CATGCC after the # sign is corresponding to the reverse
complement of the barcode sequence GGCATG

'''

def printUsageAndExit(programName):
	print >> stderr,programName,"[--barcodeListing listfile|--barcode barcode --tofile x.fastq] [OtherOptions] in.fastq ..." 
	print >> stderr,"listfile: lines of"
	print >> stderr,"barCode[tab]filename"
	print >> stderr,"[options]:"
	print >> stderr,"--append append to file instead of creating a file"
	print >> stderr,"--prefixOutFileName add prefix to out file name"
	print >> stderr,"--suffixOutFileName add suffix to out file name"
	print >> stderr,"--unclassifiedReadTo x output unclassified reads to file x"
	print >> stderr,"--editDistanceMax mx. allow max mismatch to barcode (and no tie of the best two matched)"
	print >> stderr,"--outActualCodeCount suffix. write the actual barcode counts for each uniq barcode sequence to a file of the outfile name with this suffix"
	exit(1)

def loadBarCodeListing(barCodeListing,filename):
	fil=open(filename)
	for lin in fil:
		barCode,outfile=lin.rstrip("\r\n").split("\t")
		if barCodeListing.has_key(barCode):
			print >> stderr,"barcode",barCode,"already existed. Abort"
			exit(1)
		barCodeListing[barCode]=outfile
	
	fil.close()
def writeToCurFile(curFile,content):
	if curFile:
		print >> curFile,content
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['outActualCodeCount=','editDistMax=','barcodeListing=','barcode=','tofile=','append','suffixOutFileName=','prefixOutFileName=','unclassifiedReadTo='])
	
	barCodeListing=dict() # dict[barcode]=outfile
	appendOutFile=False
	suffixOutFileName=""
	barcodeCur=""
	toFileCur=""
	unclassTo=None
	editDistanceMax=0 #default is exact match
	noTie=True
	prefixOutFileName=""
	outActualCodeCount=None
	
	for o,v in opts:
		if o=='--barcodeListing':
			loadBarCodeListing(barCodeListing,v)
		elif o=='--barcode':
			barcodeCur=v
			if barCodeListing.has_key(barcodeCur):
				print >> stderr,"barcode",barCode,"already existed. Abort"
				exit(1)
		elif o=='--tofile':
			if len(barcodeCur)<1:
				print >> stderr,"--tofile is not preceded by a --barcode argument. Abort"
				exit(1)
			
			barCodeListing[barcodeCur]=v
			barcodeCur=""
		elif o=='--append':
			appendOutFile=True
		elif o=='--suffixOutFileName':
			suffixOutFileName=v
		elif o=='--unclassifiedReadTo':
			unclassTo=v
		elif o=='--editDistMax':
			editDistanceMax=int(v)
		elif o=='--prefixOutFileName':
			prefixOutFileName=v
		elif o=='--outActualCodeCount':
			outActualCodeCount=v
			
	if len(args)==0:
		print >> stderr,"no in.fastq specified. Abort"
		printUsageAndExit(programName)
		
	#now reverseComplement the barcode listing
	newBarCodeListing=dict()
	
	for k,v in barCodeListing.items():
		newBarCodeListing[reverse_complement(k)]=v
	
	#replace
	barCodeListing=newBarCodeListing
	
	writeCount=dict()
	seqBarCodeCount=dict()
	writeCountUnclassified=0	
	
	#openFiles!
	barCodeFiles=dict()
	for barCode,toFile in barCodeListing.items():
		if appendOutFile:
			barCodeFiles[barCode]=open(prefixOutFileName+toFile+suffixOutFileName,"w+")
		else:
			barCodeFiles[barCode]=open(prefixOutFileName+toFile+suffixOutFileName,"w")
			
		writeCount[barCode]=0
		if outActualCodeCount:
			seqBarCodeCount[barCode]=dict()
	
	unclassToFile=None
	
	if unclassTo!="":
		if appendOutFile:
			unclassToFile=open(prefixOutFileName+unclassTo+suffixOutFileName,"w+")
		else:
			unclassToFile=open(prefixOutFileName+unclassTo+suffixOutFileName,"w")
	
	readname=""
	
	curFile=None
	
	

	
	
	for infile in args:
		print >> stderr,"processing",infile
		fil=open(infile)
		lino=0
		for lin in fil:
			lin=lin.rstrip("\r\n")
			if len(lin)<1:
				print >> stderr,"fastq formating error. lin has zero len. abort"
				exit(1)
				
			lino+=1
			linoMod4=lino%4
			if linoMod4==1: #seq-read-name-line
				if lin[0]!="@":
					print >> stderr,"fastq formating error. first line not starting with @. Abort"
					exit(1)
				readname=lin[1:]
				afterpound=readname.split("#")[1]
				barCodeSeq=afterpound.split("/")[0]
				#if barCodeSeq not in barCodeFiles:
				#	curFile=unclassToFile
				#	writeCountUnclassified+=1
				#else:
				#	curFile=barCodeFiles[barCodeSeq]
				#	writeCount[barCodeSeq]+=1
				#
				
				matched=findBestBarcodeMatchedEntry(barCodeFiles,barCodeSeq,editDistanceMax,noTie)
				
				if not matched:
					curFile=unclassToFile
					writeCountUnclassified+=1
				else:
					barCodeMatched,toFileObj=matched
					curFile=toFileObj #1 is the file
					writeCount[barCodeMatched]+=1
					if outActualCodeCount:
						try:
							seqBarCodeCount[barCodeMatched][barCodeSeq]+=1
						except:
							seqBarCodeCount[barCodeMatched][barCodeSeq]=1
							
				writeToCurFile(curFile,lin)
			elif linoMod4==2: #seq line
				writeToCurFile(curFile,lin)
			elif linoMod4==3: #qual-read-name-lin, put "+"
				if lin[0]!="+":
					print >> stderr,"fastq formating error. Third line not starting with +. Abort"
					exit(1)
				if len(lin)>1:
					thisRName=lin[1:]
					if thisRName!=readname:
						print >> stderr,"fastq formating error. Third line read line not consistent with first line read line. Abort"
						exit(1)
				writeToCurFile(curFile,lin)
			else: #qual line
				writeToCurFile(curFile,lin)
				
		fil.close()
	
	for barCode,toFile in barCodeFiles.items():
		toFile.close()
		
	totalProc=0
	
	
		
	#now summarize:
	for barCode,toFile in barCodeListing.items():
		totalProc+=writeCount[barCode]
		print >> stderr,writeCount[barCode],"reads within",editDistanceMax,"edits of barcode",reverse_complement(barCode),"read name tagged with family of",barCode,"written to",prefixOutFileName+toFile+suffixOutFileName,
		if outActualCodeCount:
			print >> stderr,"actual code count written to",prefixOutFileName+toFile+outActualCodeCount
			thisActualCodeCountDict=seqBarCodeCount[barCode]
			
			if appendOutFile and exists(prefixOutFileName+toFile+outActualCodeCount):
				#read in the existing code count file
				finActualCodeCount=open(prefixOutFileName+toFile+outActualCodeCount)
				for lin in finActualCodeCount:
					radCode,radCount=lin.rstrip("\r\n").split("\t")
					if radCode in thisActualCodeCountDict:
						thisActualCodeCountDict[radCode]+=int(radCount)
					else:
						thisActualCodeCountDict[radCode]=int(radCount)
						
				finActualCodeCount.close()
				
			#output
			filActualCodeCount=open(prefixOutFileName+toFile+outActualCodeCount,"w")
			for radCode,radCount in thisActualCodeCountDict.items():
				print >> filActualCodeCount,radCode+"\t"+str(radCount)
			filActualCodeCount.close()
		else:
			print >> stderr,"" #just to complete the sentence	
		
	print >> stderr,totalProc,"reads classified"
	print >> stderr,writeCountUnclassified,"reads unclassified",
	
	totalProc+=writeCountUnclassified
	if unclassToFile:
		print >> stderr,"and written to",unclassTo+suffixOutFileName
	else:
		print >> stderr,""
	print >> stderr,totalProc,"reads processed"


			
	
	