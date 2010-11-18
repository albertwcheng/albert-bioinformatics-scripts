#!/usr/bin/python

'''



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

genePred format

1) name
2) chrom
3) strand
4) txStart  g0
5) txEnd    g1
6) cdsStart  g0
7) cdsEnd    g1
8) exonCount  
9) exonStarts g0
10) exonEnds  g1

'''

from sys import *


def toStrListInPlaceRecursive(L,prefix="",suffix="",sep=","):
	emptyL=[]
	emptyT=tuple()
	emptySet=set()
	
	for i in range(0,len(L)):
			if type(L[i])==type(emptyL) or type(L[i])==type(emptyT) or type(L[i])==type(emptySet):
				L[i]=prefix+sep.join(toStrListInPlaceRecursive(L[i]))+suffix
			else:
				L[i]=str(L[i])
	return L	

def ebedFields2genePredFields(fields,score,itemRgb,options):
	try:
		chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRGB,blockCount,blockSizes,blockStarts0=fields
		chromStartG0=int(chromStartG0)
		chromEndG1=int(chromEndG1)
		thickStartG0=int(thickStartG0)
		thickEndG1=int(thickEndG1)
		blockCount=int(blockCount)
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
	
	exonStartsG0=[]
	exonEndsG1=[]
	
	for bStart0,bSize in zip(blockStarts0,blockSizes):
		exonStartsG0.append(bStart0+chromStartG0)
		exonEndsG1.append(bStart0+chromStartG0+bSize)
	
	
	genePredFields=[name,chrom,strand,chromStartG0,chromEndG1,thickStartG0,thickEndG1,blockCount,exonStartsG0,exonEndsG1]	
	toStrListInPlaceRecursive(genePredFields)
	return genePredFields
	
def genePredFields2ebedFields(fields,score,itemRgb,options):
	try:
		name,chrom,strand,txStartG0,txEndG1,cdsStartG0,cdsEndG1,exonCount,exonStartsG0,exonEndsG1=fields
		txStartG0=int(txStartG0)
		txEndG1=int(txEndG1)
		cdsStartG0=int(cdsStartG0)
		cdsEndG1=int(cdsEndG1)
		exonCount=int(exonCount)
		exonStartsG0Splits=exonStartsG0.split(",")
		exonEndsG1Splits=exonEndsG1.split(",")
		exonStartsG0=[]
		for s in exonStartsG0Splits:
			s=s.strip()
			if len(s)>0:
				exonStartsG0.append(int(s))
		exonEndsG1=[]
		for s in exonEndsG1Splits:
			s=s.strip()
			if len(s)>0:
				exonEndsG1.append(int(s))
		
		if len(exonStartsG0)!=exonCount or len(exonEndsG1)!=exonCount:
			print >> stderr,"exon count not consistent with exon starts and exon ends data"
			raise ValueError
	
	except:
		print >> stderr,"format error",fields
		raise ValueError
	
	blockSizes=[]
	blockStarts0=[]
	
	for eStartG0,eEndG1 in zip(exonStartsG0,exonEndsG1):
		blockStarts0.append(eStartG0-txStartG0)
		blockSizes.append(eEndG1-eStartG0)
	
	ebedFields=[chrom,txStartG0,txEndG1,name,score,strand,cdsStartG0,cdsEndG1,itemRgb,exonCount,blockSizes,blockStarts0]
	toStrListInPlaceRecursive(ebedFields)
	return ebedFields


def readEEBedSeq(filename):
	EEBedSeqDict=dict()
	fil=open(filename)
	for lin in fil:
		fields=lin.rstrip().split("\t")
		chrom=fields[0]
		start=int(fields[1])
		end=int(fields[2])
		seq=fields[-1] #last field
		
		try:
			chromDict=EEBedSeqDict[chrom]
		except KeyError:
			chromDict=dict()
			EEBedSeqDict[chrom]=chromDict
		
		chromDict[(start,end)]=seq
		
	fil.close()
	
	return EEBedSeqDict


def EbedFieldsToEbedSeqField(fields,eebedSeqDict):
	try:
		chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRgb,blockCount,blockSizes,blockStarts0=fields
		chromStartG0=int(chromStartG0)
		chromEndG1=int(chromEndG1)
		thickStartG0=int(thickStartG0)
		thickEndG1=int(thickEndG1)
		blockCount=int(blockCount)
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
	

	seq=""
	
	eebedSeqDictChrom=eebedSeqDict[chrom]
	
	
	for bStart0,bSize in zip(blockStarts0,blockSizes):
		exonStartG0=bStart0+chromStartG0
		exonEndG1=bStart0+chromStartG0+bSize
		try:
			seq+=eebedSeqDictChrom[(exonStartG0,exonEndG1)]
		except:
			print >> stderr,"Error in eebedSeq",chrom,":",exonStartG0,"-",exonEndG1,"not found. Abort"
			exit()
		
		
	return fields+[seq]
	


def expandEbedFieldsToBedFieldList(fields,score,itemRgb,replaceCDSPosWithTranscriptStartEnd):
	try:
		chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRgb,blockCount,blockSizes,blockStarts0=fields
		chromStartG0=int(chromStartG0)
		chromEndG1=int(chromEndG1)
		thickStartG0=int(thickStartG0)
		thickEndG1=int(thickEndG1)
		blockCount=int(blockCount)
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
	
	bedFieldList=[]
	
	for bStart0,bSize in zip(blockStarts0,blockSizes):
		exonStartG0=bStart0+chromStartG0
		exonEndG1=bStart0+chromStartG0+bSize
		
		if exonEndG1<=thickStartG0 or exonStartG0>=thickEndG1: #out of Range~!
			cdsStartForThisExon=0
			cdsEndForThisExon=0
		else:
			cdsStartForThisExon=max(thickStartG0,exonStartG0)
			cdsEndForThisExon=min(thickEndG1,exonEndG1)
		if replaceCDSPosWithTranscriptStartEnd:
			bedFields=[chrom,exonStartG0,exonEndG1,name,score,strand,chromStartG0,chromEndG1,itemRgb,1,bSize,0]
		else:	
			bedFields=[chrom,exonStartG0,exonEndG1,name,score,strand,cdsStartForThisExon,cdsEndForThisExon,itemRgb,1,bSize,0]
		toStrListInPlaceRecursive(bedFields)
		bedFieldList.append(bedFields)
	
	
	return bedFieldList

def genePredFields2exonexpandedebedFields(fields,score,itemRgb,options):
	return expandEbedFieldsToBedFieldList(genePredFields2ebedFields(fields,score,itemRgb),score,itemRgb,options.replaceCDSPosWithTranscriptStartEnd)

def printListOfFields(stream,L,sep="\t"):
	if len(L)<1:
		return
		
	if type(L[0])==type(list()):
		for subL in L:
			print >> stream,sep.join(subL)
	else:
		print >> stream,sep.join(L)
		
def convertFormat(filename,converter,score,itemRgb,options):
	fil=open(filename)
	lino=0
	for lin in fil:
		lino+=1
		fields=lin.rstrip("\r\n").split(options.FS)
		try:
			ofields=converter(fields,score,itemRgb,options)
		except ValueError:
			if options.AbortOnError:
				print >> stderr,"Abort on line #"+str(lino),fields
				exit()
			else:
				continue
		printListOfFields(stdout,ofields)
	fil.close()
	
	
def ebedToebedSeqConvert(filename,eebedseqfilename,options):
	
	eebedseqDict=readEEBedSeq(eebedseqfilename)

	fil=open(filename)
	for lin in fil:
		fields=lin.rstrip("\r\n").split(options.FS)
		try:
			ofields=EbedFieldsToEbedSeqField(fields,eebedseqDict)
		except ValueError:
			if options.AbortOnError:
				print >> stderr,"Abort on line #"+str(lino),fields
				exit()
			else:
				continue
							
		printListOfFields(stdout,ofields)
	fil.close()
	
	
if __name__=='__main__':
	from optparse import OptionParser
	
	usage="usage: %prog  [other options] filename [ebed2genePred*|--genePred2ebed|--genePred2exonebed|--ebed2exonebed|--ebed2ebedseq eebedseq]"
	parser=OptionParser(usage)
	#parser.add_option("--genePred2ebed",dest="genePred2ebed",default=False,action="store_true",help="convert genePred to ebed format")
	#parser.add_option("--genePred2exonebed",dest="genePred2exonebed",default=False,action="store_true",help="convert genePred to exon expanded ebed format")
	#parser.add_option("--ebed2exonebed",dest="ebed2exonebed",default=False,action="store_true",help="convert ebed into exon expanded ebed format")
	
	parser.add_option("--genePred2ebed",const=genePredFields2ebedFields,dest="conversion",default=ebedFields2genePredFields,action="store_const",help="convert genePred to ebed format")
	parser.add_option("--genePred2exonebed",const=genePredFields2exonexpandedebedFields,dest="conversion",default=ebedFields2genePredFields,action="store_const",help="convert genePred to exon expanded ebed format")
	parser.add_option("--ebed2exonebed",const=expandEbedFieldsToBedFieldList,dest="conversion",default=ebedFields2genePredFields,action="store_const",help="convert ebed into exon expanded ebed format")
	parser.add_option("--score",default="0",dest="score",help="set score (bed output)")
	parser.add_option("--itemRgb",default="0,0,0",dest="itemRgb",help="set itemRgb (bed output)")
	parser.add_option("--ebed2ebedseq",dest="ebedseq",default=None,help="transcribe the gene structure to make ebedseq file (with the last column as transcribed sequence)")
	#parser.conversion=genePredFields2ebedFields
	parser.add_option("--replace-Start-End-With-Transcript-Start-End",dest="replaceCDSPosWithTranscriptStartEnd",default=False,action="store_true",help="replace the CDS start end end field with transcript start and end field (valid for --ebed2exonbed)")
	parser.add_option("--abort-on-error",default=False,dest="AbortOnError",action="store_true",help="aborts on error parsing a line of input")
	parser.add_option("--fs",default="\t",dest="FS",help="set fields separator. default [tab]")
	(options,args)=parser.parse_args()
	
	

		
	try:
		filename,=args
	except:
		parser.print_help()
		exit()
		
		
		
	if options.ebedseq:
		eebedseqfilename=options.ebedseq
		ebedToebedSeqConvert(filename,eebedseqfilename,options)
	else:
		convertFormat(filename,options.conversion,options.score,options.itemRgb,options)
	
	#opsum=int(options.genePred2ebed)+int(options.genePred2exonebed)+int(options.ebed2exonebed)
		
	#if opsum==0: #do default [ebed2genePred]
		
	#elif opsum==1: #do required
	#	if options.genePred2ebed:
			
	#	elif options.genePred2exonebed:
		
	#	elif options.ebed2exonebed:
		
	#	else: #will not happen
	#		pass
	#else:
	#	print >> stderr,"please make decision, cannot perform multiple operations"
	#	parser.print_help()
	#	exit()	
	
	
	
