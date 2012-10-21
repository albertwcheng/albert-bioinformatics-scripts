#!/usr/bin/env python

from getopt import getopt
from sys import *
from Bio import AlignIO
from os import system
import os



def readFasta(filename):

	fil=open(filename)
	seqName=filename
	seq=""
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue
		if lin[0]=='>':
			seqName=lin[1:]
			continue
		seq+=onlyATCGNU(lin)
		
	fil.close()
	
	return seqName,seq


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
	print >> stderr,clustalCmd,infile
	system(clustalCmd+ " " +infile + " > "+infile+".cx.stdout")	

def numMatches(alnFile):
	align=AlignIO.read(alnFile,"clustal")
	seq1=align[0].seq
	seq2=align[1].seq
	
	numMatches=0
	for s1,s2 in zip(seq1,seq2):
		if s1.upper()==s2.upper():
			numMatches+=1
	return numMatches
	
def printUsageAndExit(programName):
	print >> stderr,programName,"[options] outfolder ref seq1 seq2 ... seqN"
	print >> stderr,"--clustal-cmd x. specify the clustal command. default: clustalw"
	print >> stderr,"--non-CpG-conversion-stat-out out. Append file"
	print >> stderr,"--non-CpG-conversion-stat-out-sample-name sampleName. default is abspath of the directory of the first aligning sequence"
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['clustal-cmd=','non-CpG-conversion-stat-out=','non-CpG-conversion-stat-out-sample-name='])
	

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
	
	nonCpGConvStatOutFile=None
	
	nonCpGConvStatOutSampleName=os.path.dirname(os.path.abspath(seqs[0]))
	
	
	for o,v in opts:
		if o=='--clustal-cmd':
			clustalCmd=v
		elif o=='--non-CpG-conversion-stat-out':
			nonCpGConvStatOutFile=v
		elif o=='--non-CpG-conversion-stat-out-sample-name':
			nonCpGConvStatOutSampleName=v

	
	if nonCpGConvStatOutFile:
		nonCpGConvStatOutFile=open(nonCpGConvStatOutFile,"a")
	
	refName,refSeq=readFasta(ref)
	
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	
	allseqSName="all"
	allFullPath=os.path.join(outfolder,allseqSName)
	foutAll=open(allFullPath+".fasta","w")
	
	print >> foutAll,">ref"
	print >> foutAll,refSeq
	
	seqIToFilenameMap=dict()
	
	
	for i in range(0,len(seqs)):
		fName="seq%dtorefF" %(i+1)
		rName="seq%dtorefR" %(i+1)
		sName="seq%dtorefS" %(i+1)
		
		
		
		testName,testSeq=readFasta(seqs[i])
		
		fNameFullPath=os.path.join(outfolder,fName)
		fout=open(fNameFullPath+".fasta","w")
		print >> fout,">ref"
		print >> fout,refSeq
		print >> fout,">test"
		print >> fout,testSeq
		fout.close()
		
		runClustalw(clustalCmd,fNameFullPath+".fasta")
		
		FNumMatches=numMatches(fNameFullPath+".aln")
		
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
		
		RNumMatches=numMatches(rNameFullPath+".aln")
		
		sNameFullPath=os.path.join(outfolder,sName)
		
		
		if FNumMatches>RNumMatches:
			nama="seq_%d_F" %(i+1)
			print >> foutAll,">"+nama
			print >> foutAll,testSeq
		else:
			nama="seq_%d_R" %(i+1)
			print >> foutAll,">"+nama
			print >> foutAll,testSeqR
			
		seqIToFilenameMap[nama]=seqs[i]
		
	foutAll.close()	
	
	runClustalw(clustalCmd,allFullPath+".fasta")
	
	
	#now analyze the master aln
	align=AlignIO.read(allFullPath+".aln","clustal")
	
	
	testAligns=[]
	
	
	
	for i in range(0,len(align)):
		if align[i].id == 'ref':
			refAlign=align[i].seq
			refAlignIdx=i #this we will delete from the final profile
		else:
			testAligns.append(align[i].seq)
	
	profile=[]
	profileNames=[]
	for i in range(0,len(align)):
		profile.append([])
		profileNames.append(align[i].id)
		
	profilePos=[]
	
	profileNumM=[] #number of M'ed seq per position
	profileNumI=[] #number of Informative seq per position
	
	CGNumM=0
	CGNumI=0
	
	nonCGConv=0 #number of C is converted to T not followed by G
	nonCGI=0 #number of C position not followed by G
	
	prevI=-1
	prevN=""
	for i in range(0,len(refAlign)):
		thisN=refAlign[i].upper()
		if thisN in ["A","C","G","T"]:
			#print >> stderr,prevN+thisN
			if prevN+thisN=="CG":
				##a CpG found!
				#look at prevI column for C->T
				profilePos.append(str(prevI+1))
				columnStr=align[:,prevI].upper()
				
				numM=0
				numI=0
				
				for j in range(0,len(profile)):
					if columnStr[j]=="T":
						profile[j].append("0")
						numI+=1
					elif columnStr[j]=="C":
						profile[j].append("1")
						numI+=1
						numM+=1
					else:
						profile[j].append("-")
					
				
				profileNumM.append(numM-1) #has to minus one, because of the ref
				profileNumI.append(numI-1) #has to minus one, because of the ref
				
				CGNumM+=numM-1 #keep total
				CGNumI+=numI-1
				
			elif prevN+thisN in ["CT","CA","CC"]: #non-CpG position for estimating conversion efficiency
				#print >> stderr,"heythere"
				columnStr=align[:,prevI].upper()
				#print >> stderr,columnStr
				for j in range(0,len(profile)):
					if j!=refAlignIdx:
						if columnStr[j]=="T":
							#converted
							nonCGConv+=1
							nonCGI+=1
						elif columnStr[j]=="C":
							nonCGI+=1

										
						
			prevN=thisN
			prevI=i
			
	
	del profile[refAlignIdx]
	del profileNames[refAlignIdx]
	
	
	
	profileOut=os.path.join(outfolder,"profile.xls")
	profout=open(profileOut,"w")
	print >> profout, "\t".join(["file"]+profilePos)
	for profName, prof in zip(profileNames,profile):
		print >> profout,  "\t".join([seqIToFilenameMap[profName]]+prof)
	profout.close()
	
	profilePercentages=os.path.join(outfolder,"profile_percentages.xls")
	profilePerOut=open(profilePercentages,"w")
	print >> profilePerOut,"CpGPos\t%M\tfM\t#M\t#InfSeq"
	for pPos,pM,pI in zip(profilePos,profileNumM,profileNumI):
		try:
			print >> profilePerOut, "%s\t%f%%\t%f\t%d\t%d" %(pPos,float(pM)/pI*100,float(pM)/pI,pM,pI)
		except:
			print >> profilePerOut, "%s\t%s\t%s\t%d\t%d" %(pPos,"NA","NA",pM,pI)
		
	print >> profilePerOut, "%s\t%f%%\t%f\t%d\t%d" %("TotalCpG",float(CGNumM)/CGNumI*100,float(CGNumM)/CGNumI,CGNumM,CGNumI)
	try:
		print >> profilePerOut, "%s\t%f%%\t%f\t%d\t%d" %("NonCpGConversionRate",float(nonCGConv)/nonCGI*100,float(nonCGConv)/nonCGI,nonCGConv,nonCGI)
	except:
		print >> profilePerOut, "%s\t%s\t%s\t%d\t%d" %("NonCpGConversionRate","NA","NA",nonCGConv,nonCGI)
	if nonCpGConvStatOutFile:
		try:
			print >> nonCpGConvStatOutFile, "%s\t%f%%\t%f\t%d\t%d" %(nonCpGConvStatOutSampleName,float(nonCGConv)/nonCGI*100,float(nonCGConv)/nonCGI,nonCGConv,nonCGI)
		except:
			print >> nonCpGConvStatOutFile, "%s\t%s%%\t%s\t%d\t%d" %("NonCpGConversionRate","NA","NA",nonCGConv,nonCGI)
	
	profilePerOut.close()
	

	
	profilePlotOut=os.path.join(outfolder,"profile.pdf")
	system("plotColorMap.py --xtick-rotation 90 --color-map gist_gray_r %s %s" %(profileOut,profilePlotOut) )
	
	if nonCpGConvStatOutFile:
		nonCpGConvStatOutFile.close()	
	