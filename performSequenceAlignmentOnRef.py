#!/usr/bin/env python

from getopt import getopt
from sys import *
from Bio import AlignIO
from os import system
import os
from termcolor import colored


def hasPrefix(haystack,needle):
	if len(haystack)<len(needle):
		return False
	
	return haystack[0:len(needle)]==needle

def genericReadSequenceFile(filename,commentGrepper=""):
	mode='P' #P=PLAIN, G=GENBANK, F=FASTA
	fil=open(filename)
	seqName=filename
	seq=""
	lino=0
	originStarted=False
	comments=[]
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue
		lino+=1
		
		if lino==1:
			if hasPrefix(lin,"LOCUS"):
				locusSplit=lin.split()
				try:
					seqName=locusSplit[1]
				except:
					pass
				mode='G'
			elif lin[0]=='>':
				seqName=lin[1:]
				mode='F'
			else:
				seq+=onlyATCGNU(lin)
		else:	
			
			if mode in ('F','P'):
				seq+=onlyATCGNU(lin)
			elif mode == 'G':
				
				if hasPrefix(lin,"COMMENT"):
					commentSplit=lin.split()
					try:
						comments.append(commentSplit[1])
					except:
						pass
				elif commentGrepper in lin:
					comments.append(lin.strip())
				elif hasPrefix(lin,"ORIGIN"):
					originStarted=True
				elif hasPrefix(lin,"//"):
					break
				elif originStarted:
					seq+=onlyATCGNU(lin)
				
	fil.close()
	
	return seqName,seq,comments


	


def onlyATCGNU(seq):
	reta=""
	for s in seq:
		if s.upper() in ['A','C','T','G','N','U']:
			reta+=s
	return reta

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


def runClustalw(clustalCmd,infile):
	#print >> stderr,clustalCmd,infile
	system(clustalCmd+ " " +infile + " > "+infile+".cx.stdout")	

def findLongestStretchOfIdenticalMatches(alnFile):
	align=AlignIO.read(alnFile,"clustal")
	seq1=align[0].seq
	seq2=align[1].seq
	
	numMatches=0
	
	longestMatches=-1
	longestMatchStart1=-1
	longestMatchEnd1=-1
	longestMatchStart2=-1
	longestMatchEnd2=-1
	longestMatchSeqS1=""
	longestMatchSeqS2=""
	
	currentMatchStart1=-1
	currentMatchStart2=-1
	currentMatchSeq=""
	
	i1=-1
	i2=-1
	
	for s1,s2 in zip(seq1,seq2):
		if s1!="-":
			i1+=1
		if s2!="-":
			i2+=1
		
		if s1.upper()==s2.upper():
			numMatches+=1
			if numMatches==1:
				currentMatchStart1=i1
				currentMatchStart2=i2
				currentMatchSeqS1=s1
				currentMatchSeqS2=s2
			else:
				currentMatchSeqS1+=s1
				currentMatchSeqS2+=s2
		else: #not matched
			if numMatches>0 and numMatches>longestMatches:
				longestMatches=numMatches
				longestMatchStart1=currentMatchStart1
				longestMatchStart2=currentMatchStart2
				longestMatchEnd1=i1
				longestMatchEnd2=i2
				longestMatchSeqS1=currentMatchSeqS1
				longestMatchSeqS2=currentMatchSeqS2
				
			numMatches=0
				
	#ending
	if numMatches>0 and numMatches>longestMatches:
		longestMatches=numMatches
		longestMatchStart1=currentMatchStart1
		longestMatchStart2=currentMatchStart2
		longestMatchEnd1=i1+1
		longestMatchEnd2=i2+1
		longestMatchSeqS1=currentMatchSeqS1
		longestMatchSeqS2=currentMatchSeqS2
	
	#if longestMatchEnd1-longestMatchStart1!=longestMatches:
	#	print >> stderr,"error: longestMatch 1 BoundNotConsistent",longestMatchEnd1,longestMatchStart1,longestMatches
	#if longestMatchEnd2-longestMatchStart2!=longestMatches:
	#	print >> stderr,"error: longestMatch 2 BoundNotConsistent",longestMatchEnd2,longestMatchStart2,longestMatches
	
	return (longestMatches,align[0].id,align[1].id,longestMatchStart1,longestMatchStart2,longestMatchSeqS1,longestMatchSeqS2)
	
def highlightSubSeq(seq,subseq,color,attrs):
	
	seqU=seq.upper()
	subseqU=subseq.upper()
	subseqL=len(subseqU)
	
	while True:
		found=seqU.rfind(subseqU)
		if found<0:
			break
		
		#"\x1b[5m\x1b[7m\x1b[32m" "\x1b[0m"
		seq=seq[:found]+colored(seq[found:found+subseqL],color,attrs=attrs)+seq[found+subseqL:]	
		
		seqU=seqU[:found]
		
	return seq
	
def printUsageAndExit(programName):
	print >> stderr,programName,"[options] outfolder ref seq1 seq2 ... seqN"
	print >> stderr,"What it does: align seq1...seqN onto ref, find the longest stretch of alignments per seq"
	print >> stderr,"--clustal-cmd x. specify the clustal command. default: clustalw"
	print >> stderr,"--highlight seq. specify sequence to highlights. Can repeat this option"
	print >> stderr,"--highlight-color. specify highlight color. preceed --highlight to be effective"
	print >> stderr,"--highlight-attrs. specify highlight attrs, e.g., blink, reverse. Preceed --highlight to be effective"	
	print >> stderr,"Alternatively highlights are specified in ref if given in genbank file as e.g., COMMENT     Highlight:GGGTCGAATTCGCCCTT:green:reverse,blink"
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['clustal-cmd=','highlight=','highlight-color=','highlight-attrs='])
	

	try:
		outfolder=args[0]
		ref=args[1]
		seqs=args[2:]
		if len(seqs)<1:
			print >> stderr,"no seq specified. abort"
			printUsageAndExit(programName)
	except:
		printUsageAndExit(programName)
	

	clustalCmd='clustalw'
	
	highlights=[]
	highlightColor="green"
	highlightAttrs=["blink","reverse"]
	for o,v in opts:
		if o=='--clustal-cmd':
			clustalCmd=v
		elif o=='--highlight':
			highlights.append([v,highlightColor,highlightAttrs])
		elif o=='--highlight-color':
			highlightColor=v
		elif o=='--highlight-attrs':
			highlightAttrs=v.split(",")
			
	refName,refSeq,refComments=genericReadSequenceFile(ref,"Highlight:")
	
	for comment in refComments:
		if hasPrefix(comment,"Highlight:"):
			commentS=comment.split(":")
			highlights.append([commentS[1],commentS[2],[] if commentS[3]=="" else commentS[3].split(",")])
			
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	

	
	
	for i in range(0,len(seqs)):
		fName="seq%dtorefF" %(i+1)
		rName="seq%dtorefR" %(i+1)
		sName="seq%dtorefS" %(i+1)
		
		
		
		testName,testSeq,comments=genericReadSequenceFile(seqs[i])
		
		fNameFullPath=os.path.join(outfolder,fName)
		fout=open(fNameFullPath+".fasta","w")
		print >> fout,">ref"
		print >> fout,refSeq
		print >> fout,">test"
		print >> fout,testSeq
		fout.close()
		
		runClustalw(clustalCmd,fNameFullPath+".fasta")
		
		(FnumMatches,FID1,FID2,FmatchStart1,FmatchStart2,FmatchSeq1,FmatchSeq2)=findLongestStretchOfIdenticalMatches(fNameFullPath+".aln")
		
		#reverse complement
		testSeqR=reverse_complement(testSeq)
		rNameFullPath=os.path.join(outfolder,rName)
		fout=open(rNameFullPath+".fasta","w")
		print >> fout,">ref"
		print >> fout,refSeq
		print >> fout,">test"
		print >> fout,testSeqR
		fout.close()
		
		runClustalw(clustalCmd,rNameFullPath+".fasta")
		
		(RnumMatches,RID1,RID2,RmatchStart1,RmatchStart2,RmatchSeq1,RmatchSeq2)=findLongestStretchOfIdenticalMatches(rNameFullPath+".aln")
		
		if FnumMatches>RnumMatches:
			start=FmatchStart1 if FID1=="ref" else FmatchStart2
			seq=FmatchSeq1 if FID1=="ref" else FmatchSeq2
			start+=1 #to base1
			end=start+FnumMatches-1
			dire="F"
			
		else:
			start=RmatchStart1 if RID1=="ref" else RmatchStart2
			seq=RmatchSeq1 if RID1=="ref" else RmatchSeq2
			start+=1 #to base1
			dire="R"
			end=start+RnumMatches-1
			
		
		for higseq,color,attrs in highlights:
			seq=highlightSubSeq(seq,higseq,color,attrs)
			
		
			
		print >> stdout,"%s\t%s\t%s\t%d\t%d\t%s" %(ref,seqs[i],dire,start,end,seq)

	

	