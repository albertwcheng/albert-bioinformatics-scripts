#!/usr/bin/env python

from sys import *
from getopt import getopt

complDict={'A':'T','a':'t','C':'G','c':'g','T':'A','t':'a','G':'C','g':'c','U':'A','u':'a'}	
	
	
def complementBase(c):
	global complDict
	try:
		return complDict[c]
	except:
		return c

		
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
	print >> stderr,"--suffixOutFileName add suffix to out file name"
	print >> stderr,"--unclassifiedReadTo x output unclassified reads to file x"
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
	opts,args=getopt(argv[1:],'',['barcodeListing=','barcode=','tofile=','append','suffixOutFileName=','unclassifiedReadTo='])
	
	barCodeListing=dict() # dict[barcode]=outfile
	appendOutFile=False
	suffixOutFileName=""
	barcodeCur=""
	toFileCur=""
	unclassTo=None
	
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
	writeCountUnclassified=0	
	
	#openFiles!
	barCodeFiles=dict()
	for barCode,toFile in barCodeListing.items():
		if appendOutFile:
			barCodeFiles[barCode]=open(toFile+suffixOutFileName,"w+")
		else:
			barCodeFiles[barCode]=open(toFile+suffixOutFileName,"w")
			
		writeCount[barCode]=0
	
	unclassToFile=None
	
	if unclassTo!="":
		if appendOutFile:
			unclassToFile=open(unclassTo+suffixOutFileName,"w+")
		else:
			unclassToFile=open(unclassTo+suffixOutFileName,"w")
	
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
				if barCodeSeq not in barCodeFiles:
					curFile=unclassToFile
					writeCountUnclassified+=1
				else:
					curFile=barCodeFiles[barCodeSeq]
					writeCount[barCodeSeq]+=1
				
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
		print >> stderr,writeCount[barCode],"reads with barcode",reverse_complement(barCode),"labeled as",barCode,"written to",toFile+suffixOutFileName
	
	print >> stderr,totalProc,"reads classified"
	print >> stderr,writeCountUnclassified,"reads unclassified",
	
	totalProc+=writeCountUnclassified
	if unclassToFile:
		print >> stderr,"and written to",unclassTo+suffixOutFileName
	else:
		print >> stderr,""
	print >> stderr,totalProc,"reads processed"

	
	