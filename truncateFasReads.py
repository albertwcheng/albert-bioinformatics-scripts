#!/usr/bin/python

#split read into x bp, discarding <x bp reads

from sys import *
from optparse import OptionParser
import random

def printUsageAndExit(parser):
	parser.print_help(stderr)
	exit()

def invalidateSeqStruct(seqstruct):
	seqstruct[0]=""
	seqstruct[1]=""
	seqstruct[2]=""
	seqstruct[3]=0	
	
	return seqstruct

def trimNInSeqStruct(seqstruct):
	tag,seq,qual,state=seqstruct
	if len(seq)==0:
		return
		
	if len(seq)==len(qual):
		#find last N in prefix of seq in base-1  => i
		i=0 #this is useless actually
		for x in range(0,len(seq)):
			i=x
			if seq[x].upper()!='N':
				break
		
		if i==len(seq)-1:
			invalidateSeqStruct(seqstruct)
			return
		#find last N in seq from end  => j
		j=len(seq)
		for x in range(len(seq)-1,-1,-1):
			if seq[x].upper()!='N':
				break
			j-=1
		
		seqstruct[1]=seq[i:j]
		seqstruct[2]=qual[i:j]
	
def outputSeq(seqstruct,trunclength,subSeqSelector,options,parser,trimN):
	#print >> stderr,seqstruct

	
	tag,seq,qual,state=seqstruct
	if len(qual)>0 and len(seq)>0 and len(qual)!=len(seq):
		print >> stderr,"error: seq is not same length as qual string"
		exit()
	
	if trimN:
		trimNInSeqStruct(seqstruct)
		
	if len(seq)<1:
		#print >> stderr,"lenseq<1"
		invalidateSeqStruct(seqstruct)
		return
	
	#print >> stderr,seqstruct
	
	subSeqSelector(seqstruct,trunclength,options,parser)	
	tag,seq,qual,state=seqstruct
	
	#print >> stderr,seqstruct
	
	if len(seq)>0:  #if seq is set to invalid skip all these steps of outputing
		if len(qual)>0 and len(seq)>0 and len(qual)!=len(seq):
			print >> stderr,"error: seq is not same length as qual string"
			exit()	
				
					
		if len(qual)>0:
			print >> stdout,"@"+tag #this is a fastq
		else:
			print >> stdout,">"+tag #this is a fasta
					
		print >> stdout,seq
					
		if len(qual)>0:
			print >> stdout,"+"
			print >> stdout,qual
				
	#reinit seqstruct
	invalidateSeqStruct(seqstruct)




def getSeqStructAtPosInPlace(seqstruct,i,trunclength):
	tag,seq,qual,state=seqstruct
	if i+trunclength>len(seq) or i<0:
		#invalid
		invalidateSeqStruct(seqstruct)
	else:
		seqstruct[1]=seq[i:i+trunclength]
		if len(qual)>0: #has quality
			seqstruct[2]=qual[i:i+trunclength]
	
	return seqstruct

###subSeqSelectors:  (in place)

def atPos(seqstruct,trunclength,options,parser):
	return getSeqStructAtPosInPlace(seqstruct,options.atPos-1,trunclength)

def atMiddle(seqstruct,trunclength,options,parser):
	tag,seq,qual,state=seqstruct
	return getSeqStructAtPosInPlace(seqstruct,(len(seq)-trunclength)/2,trunclength)


def randomPos(seqstruct,trunclength,options,parser):
	tag,seq,qual,state=seqstruct
	upperBound=len(seq)-trunclength  #upperBound is inclusive random.randint is inclusive on both bounds
	if upperBound<0:
		#invalid
		return invalidateSeqStruct(seqstruct)
	
	return getSeqStructAtPosInPlace(seqstruct,random.randint(0,upperBound),trunclength)

def bestQual(seqstruct,trunclength,options,parser):
	tag,seq,qual,state=seqstruct
	
	if len(seq)<1:
		return
	
	if len(seq)!=len(qual) or len(qual)<1:
		print >> stderr,"invalid format. --best-qual option is only valid for files with quality scores (fastq files). Abort",len(seq),len(qual)
		printUsageAndExit(parser)
	
	#now do the trick here
	
	maxTPos=0
	maxT=0 #relative to the first position [0]
	
	Ti_1=0
	
	for i in range(1,len(qual)-trunclength+1): #from 1 to seqlength-trunclength inclusive
		Ti=Ti_1+ord(qual[i+trunclength-1])-ord(qual[i-1])
		if Ti>maxT:
			maxT=Ti
			maxTPos=i
		
		Ti_1=Ti #for next round
		
	#now maxTPos is the position where the qual is maximized
	return getSeqStructAtPosInPlace(seqstruct,maxTPos,trunclength)	
		
if __name__=='__main__':

	usage="Usage: %prog [--at-pos 1*|--random-pos|--best-qual|--at-middle] filename desiredLength"
	parser=OptionParser(usage)
	
	parser.add_option("--at-pos",dest="atPos",default=1,type="int",help="get the subsequence starting at the specified position [default method]. default position 1")
	parser.add_option("--at-middle",dest="subseqSelector",default=atPos,const=atMiddle,action="store_const",help="get the subsequence at the middle away the two end")
	parser.add_option("--random-pos",dest="subseqSelector",default=atPos,const=randomPos,action="store_const",help="get the subsequence at a random possible position")
	parser.add_option("--best-qual",dest="subseqSelector",default=atPos,const=bestQual,action="store_const",help="get the subsequence with the total base quality score (only possible with fastq file with quality scores)")
	parser.add_option("--trim-N",dest="trimN",default=False,action="store_true",help="trim N from head and tail of sequences before any operations")
	
	(options,args)=parser.parse_args()
	
	try:
		filename,trunclength=args
	except:
		printUsageAndExit(parser)
	
	trunclength=int(trunclength)
	seqstruct=["","","",-1] #tag,seq,qual
	
	lino=0
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)==0:
			continue
		
		lino+=1
			
		if lino%2==1:
			if lin[0] in ['>','@']:
				outputSeq(seqstruct,trunclength,options.subseqSelector,options,parser,options.trimN)
				seqstruct[0]=lin[1:]
			elif lin[0] in ["+"]:
				seqstruct[3]=1
			else:
				print >> stderr,"invalid formating at",lino,lin
		else:
			if seqstruct[3]==0:
				#get sequence
				seqstruct[1]+=lin
			else:
				#get quality string
				seqstruct[2]+=lin			
		
		
	fil.close()
	
	#output the last bit
	outputSeq(seqstruct,trunclength,options.subseqSelector,options,parser,options.trimN)
	