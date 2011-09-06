#!/usr/bin/env python

from bedFunc import *
from ORFFinder import findORFInThreeFrames
from optparse import OptionParser
from albertcommon import *
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

def findUORFsFromBedSeqFields(fields,options):

	uORFS=[] #gStart0,gEnd1,tStart0,tEnd1,seq

	try:
		chrom,chromStartG0,chromEndG1,name,score,strand,thickStartG0,thickEndG1,itemRGB,blockCount,blockSizes,blockStarts0,transcriptSeq=fields
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
	
	#check if no main orf, then do nothing
	if thickStartG0<0 or  thickEndG1<0 or thickStartG0>=thickEndG1:
		#no main orf
		return name,chrom,chromStartG0,strand,uORFS
	
	
	if strand=="+":
		#forward strand
		mainORFStartTCoord=genomicCoordToTranscriptCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,thickStartG0)
	elif strand=="-":
		mainORFStartTCoord=genomicCoordToTranscriptCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,thickEndG1-1,True)
	else:
		print >> stderr,"invalid strand",fields
		raise ValueError
	
	
		
	ranges=findORFInThreeFrames(transcriptSeq,False,options.minORFLength,options.maxORFLength) #findLongestORF=False #ranges=(start0,end1) in nt., not including Stop codon
	
	if ranges==None:
		#nothing found. return
		return name,chrom,chromStartG0,strand,uORFS
	
	for rang in ranges:
		realrangeIncStop=(rang[0],rang[1]+3)
		#now need the ORF before mainORFSTart
		#this is sorted. so if >=mainORFSTart, break
		if realrangeIncStop[0]>=mainORFStartTCoord:
			break
		
		distToCDS=mainORFStartTCoord-realrangeIncStop[0]
		
		if realrangeIncStop[1]>mainORFStartTCoord: #stop after main orf start, check phase needs to be different (i.e., out of frame)
			if distToCDS % 3 == 0: #in frame, skip
				continue
		
		#now the remaining are the OK Uorfs~
		#HERE
		uORFSeq=transcriptSeq[realrangeIncStop[0]:realrangeIncStop[1]]
		if realrangeIncStop[0]-3>=0:
			minus3Base=transcriptSeq[realrangeIncStop[0]-3]
		else:
			minus3Base="NA"
		
		plus4Base=transcriptSeq[realrangeIncStop[0]+4-1]
		
		if strand=="+":
			uORFgStart0=transcriptCoordToGenomicCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,realrangeIncStop[0])
			uORFgEnd1=transcriptCoordToGenomicCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,realrangeIncStop[1]-1)+1
		else:
			uORFgStart0=transcriptCoordToGenomicCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,realrangeIncStop[1]-1,True)
			uORFgEnd1=transcriptCoordToGenomicCoordBedFormatted(chromStartG0,blockStarts0,blockSizes,realrangeIncStop[0],True)+1
		
		
		
		clipBlockStarts,clipBlockSizes=clipBlocksByGenomicBound(chromStartG0,blockStarts0,blockSizes,uORFgStart0,uORFgEnd1,True)	
		#transform clipblock starts by referencing first block from 0 Last option=True
		
		
					
		uORFS.append((uORFgStart0,uORFgEnd1,realrangeIncStop[0],realrangeIncStop[1],clipBlockStarts,clipBlockSizes,uORFSeq,distToCDS,minus3Base,plus4Base))
		#what should we do here?!?!?
	
	return name,chrom,chromStartG0,strand,uORFS
	
def printUsageAndExit(parser):
	parser.print_help()
	exit(1)	

if __name__=='__main__':
	
	parser=OptionParser(usage="Usage: %prog inbed ogbed oinfo")
	parser.add_option("--minORFLength",dest="minORFLength",default=-1,type="int",help="set min ORF length for uORFs")
	parser.add_option("--maxORFLength",dest="maxORFLength",default=-1,type="int",help="set max ORF length for uORFs")
	parser.add_option("--trackName",dest="trackName",default="uORFs",help="set track name for output bed file")
	parser.add_option("--trackDescription",dest="trackDescription",default="upstream open reading frames",help="set track description for output bed file")
	parser.add_option("--trackVisilibity",dest="trackVisibility",default="full",help="set track visibility")
	
	(options,args)=parser.parse_args()
	
	try:
		filename,ogbedfn,oinfofn=args
	except:
		printUsageAndExit(parser)
	
	ogbed=open(ogbedfn,"w")
	oinfo=open(oinfofn,"w")
	
	print >> ogbed,"track name='"+options.trackName+"' description='"+options.trackDescription+"' visibility='"+options.trackVisibility+"'"
	print >> oinfo,"uORFName\tuORFSeq\tuORFTranslation\tuORFLengthNt\tDistanceToCDS\tminus3Base\tplus4Base"
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=="#":
			continue
		
		fields=lin.split("\t")
		name,chrom,geneChromStart0,strand,uORFS=findUORFsFromBedSeqFields(fields,options)
		for i in range(0,len(uORFS)):
			uORFgStart0,uORFgEnd1,tStart0,tEnd1,clipBlockStarts,clipBlockSizes,uORFSeq,distToCDS,minus3Base,plus4Base=uORFS[i]
			clipBlockStartStr=",".join(toStrList(clipBlockStarts))
			clipBlockSizeStr=",".join(toStrList(clipBlockSizes))
			outputv=toStrList([chrom,uORFgStart0,uORFgEnd1,name+".uORF"+str(i+1),0,strand,uORFgStart0,uORFgEnd1,"0,0,0",len(clipBlockStarts),clipBlockSizeStr,clipBlockStartStr])
			print >> ogbed,"\t".join(outputv)
			coding_dna=Seq(uORFSeq,generic_dna)
			protein_seq=coding_dna.translate(to_stop=True)
			print >> oinfo,"\t".join(toStrList([name+".uORF"+str(i+1),uORFSeq,protein_seq,len(uORFSeq),distToCDS,minus3Base,plus4Base]))
		
		
	fil.close()
	ogbed.close()
	oinfo.close()