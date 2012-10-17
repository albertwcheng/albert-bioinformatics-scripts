#!/usr/bin/env python

from albertcommon import *
from sys import *
from BedSeqUtil import BedSeqClient

def intWithComma(S):
	return int(S.replace(",",""))

def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"SNPTable colChr colCoordinate colAlleleA colAlleleB leftGet rightGet seqDir"
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		SNPTable,colChr,colCoordinate,colAlleleA,colAlleleB,leftGet,rightGet,seqDir=args
	except:
		printUsageAndExit(programName)
		
	
	headerRow=1
	startRow=2
	fs="\t"
	header,prestarts=getHeader(SNPTable,headerRow,startRow,fs)
	
	leftGet=int(leftGet)
	rightGet=int(rightGet)
	
	colChr=getCol0ListFromCol1ListStringAdv(header,colChr)[0]
	colCoordinate=getCol0ListFromCol1ListStringAdv(header,colCoordinate)[0]
	colAlleleA=getCol0ListFromCol1ListStringAdv(header,colAlleleA)[0]
	colAlleleB=getCol0ListFromCol1ListStringAdv(header,colAlleleB)[0]
	
	labelASeq=header[colAlleleA]+".seq"
	labelBSeq=header[colAlleleB]+".seq"
	
	header+=[labelASeq,labelBSeq]
	
	print >> stdout,fs.join(header)
	
	bedSeqClient=BedSeqClient(seqDir,"bed")
	
	lino=0
	
	fil=open(SNPTable)
	for lin in fil:
		lino+=1
		
		if lino<startRow:
			continue
		
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
	
		chrom=fields[colChr]
		if "chr" not in chrom:
			chrom="chr"+chrom
			
		coord=intWithComma(fields[colCoordinate])
		alleleA=fields[colAlleleA]
		alleleB=fields[colAlleleB]
		
		if leftGet>=coord:
			leftGet=coord-1
		
		leftBound=coord-leftGet
		rightBound=coord+rightGet
		
		
		
		bedSeqResult=bedSeqClient.getBedSeq(chrom+"\t"+str(leftBound-1)+"\t"+str(rightBound))
		seqGot=bedSeqResult.split("\t")[3].upper()
		
		alleleGotNt=seqGot[leftGet] #if 0, then get the 0th char, if 1, then get the 1th char
		
		if alleleGotNt not in [alleleA,alleleB]:
			print >> stderr,"error: allele info not consistent with genome seq lino=%d GenomeSeq=%s alleleGot=%s alleleA=%s alleleB=%s coordSNP=%s:%d-%d coordBound=%s:%d-%d" %(lino,seqGot,alleleGotNt,alleleA,alleleB,chrom,coord,coord,chrom,leftBound,rightBound)
			exit(1)
	
		alleleASeq=seqGot[:leftGet]+alleleA+seqGot[leftGet+1:]
		alleleBSeq=seqGot[:leftGet]+alleleB+seqGot[leftGet+1:]
		
		fields+=[alleleASeq,alleleBSeq]
		
		print >> stdout,fs.join(fields)
	
	fil.close()
	
	bedSeqClient.close()