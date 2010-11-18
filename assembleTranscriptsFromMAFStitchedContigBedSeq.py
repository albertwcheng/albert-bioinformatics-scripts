#!/usr/bin/python

from sys import *
from BedSeqUtil import *

def getGappedLenForUngappedK(S,k):
	l=0
	U=""
	if k<=0:
		return 0
		
	for i in range(0,len(S)):
		s=S[i]
		if s!="-":
			l+=1
	
		if l==k:
			return i+1
	
	return len(S)
	
complDict={'A':'T','a':'t','C':'G','c':'g','T':'A','t':'a','G':'C','g':'c','U':'A','u':'a'}	
	
	
def complementBase(c):
	global complDict
	try:
		return complDict[c]
	except:
		return c

def getSeqsArrayByExtractingRefSeqAndGapNonRefSeq(refGenomeBedSeqClient,genomes,chrom,thisSeqStart,thisSeqEnd):
	thisSeqLength=thisSeqEnd-thisSeqStart
	refSeq=refGenomeBedSeqClient.getSeq([chrom,thisSeqStart,thisSeqEnd]) #(get genome +ve strand)
			
	if len(refSeq)!=thisSeqLength:
		print >> stderr,"error: bed seq error. abort"
		exit()	
	
	gappedNonReferenceString=thisSeqLength * "-"
			
	seqs=[refSeq] #fill in reference sequence (genome +ve strand) from reference genome
	for k in range(1,len(genomes)):
		seqs.append(gappedNonReferenceString)
	
	return seqs
		
def reverse_complement(S):
	rc=""
	for i in range(len(S)-1,-1,-1):
		rc+=complementBase(S[i])
	
	return rc
	

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	exonData=dict()
	
	
	try:
		filename,genomes,refGenomeSeqDir=args
	except:
		print >> stderr,programName,"bedfile genomes refGenomeSeqDir > assembledSeqBed"
		exit()
		
	#ok, start a ref genome bed seq client (open as bed-input format)
	refGenomeBedSeqClient=BedSeqClient(refGenomeSeqDir,"bed")
		
	genomes=genomes.split(",")
	
	print >> stdout,"transcriptID\t"+"\t".join(genomes)
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
	
		if len(fields)<8:
			print >> stderr,"invalid number of fields. abort"
			exit()
			
		chrom=fields[0]
		thisExonStart=int(fields[1])
		thisExonEnd=int(fields[2])

		transcript=fields[3]
		thisStrand=fields[5]
		thisTranscriptStart=int(fields[6])
		thisTranscriptEnd=int(fields[7])
		
		if len(fields)>=9:
			if len(fields)!=15+len(genomes):
				print >> stderr,"invalid number of fields. abort. Not consistent with the nubmer of genomes"
				exit()
			thisSeqStart=int(fields[13])
			thisSeqEnd=int(fields[14])
			seqs=fields[15:]
		else:
			#to solve the non-covered exon problem
			print >> stderr,"exon with start="+str(thisExonStart)+" and end="+str(thisExonEnd)+" for transcript",transcript,"has no sequence data. fill in from ref genome and gap non-ref seqs"
			thisSeqStart=thisExonStart
			thisSeqEnd=thisExonEnd
			seqs=getSeqsArrayByExtractingRefSeqAndGapNonRefSeq(refGenomeBedSeqClient,genomes,chrom,thisExonStart,thisExonEnd)
		
		try:
			exonDataForTranscript,strand,transcriptStart,transcriptEnd=exonData[transcript]
			if thisStrand!=strand:
				print >> stderr,"inconsistent strand, abort",thisStrand,strand,lin
				exit()
				
			if thisTranscriptStart!=transcriptStart or thisTranscriptEnd!=transcriptEnd:
				print >> stderr,"inconsistent transcript start end",thisTranscriptStart,transcriptStart,thisTranscriptEnd,transcriptEnd
				exit()
				
		except:
			exonDataForTranscript=dict()
			exonData[transcript]=[exonDataForTranscript,thisStrand,thisTranscriptStart,thisTranscriptEnd]
		
		try:
			blockSeqs,exonEnd=exonDataForTranscript[thisExonStart]
			if exonEnd!=thisExonEnd:
				print >> stderr,"inconsistent exon end. abort"
				exit()
		except:
			blockSeqs=dict()
			exonEnd=thisExonEnd
			exonDataForTranscript[thisExonStart]=[blockSeqs,exonEnd]
		
		#now if blockStart is not there yet, add it, or the sequences span are longer, replace it
		if thisSeqStart not in blockSeqs or blockSeqs[thisSeqStart][0]<thisSeqEnd:
			blockSeqs[thisSeqStart]=[thisSeqEnd]+seqs
		
		
		
	fil.close()
	
	#finish reading, now for each transcript, assemble it!
	for transcript,dummy1 in exonData.items():
		exonDataForTranscript,strand,transcriptStart,transcriptEnd=dummy1
		#first assume success:
		success=True
		Errors=[]
		#now go deeper
		for exonStart,dummy2 in exonDataForTranscript.items():
			
			if not success: #some error has occured:
				break
			
			blockSeqs,exonEnd=dummy2
			#now sort blockSeqs key
			blockSeqsStarts=blockSeqs.keys()
			blockSeqsStarts.sort()
			#now assemble from end
			assembledSeqs=[]
			prevStart=-1000
			
			

			
			
			
			
			#need to use the one that span more from an earlier to solve the gap problem
			#    [       ]   [      ]
			#  [             ]
			#
			#
			
			toDeleteBlocks=set()
			
			for i in range(0,len(blockSeqsStarts)):
				if i in toDeleteBlocks:
					continue #no need to think about those already marked for deletion
				thisSeqStart=blockSeqsStarts[i]
				thisBlockSeqs=blockSeqs[thisSeqStart]
				thisSeqEnd=thisBlockSeqs[0] #this store the end of seq
				for j in range(i+1,len(blockSeqsStarts)):
					nextSeqStart=blockSeqsStarts[j]
					nextBlockSeqs=blockSeqs[nextSeqStart]
					nextSeqEnd=nextBlockSeqs[0]
					if thisSeqEnd>=nextSeqEnd:
						#can remove this block
						toDeleteBlocks.add(j)
					#else: #thisSeqend<nextSeqEnd  #REMOVED: handle later
						#if j==i+1:
							#if thisSeqEnd<nextSeqStart:	
								#hole between seq blocks:
								#Errors.append("Hole Between MAF blocks for transcript="+transcript+" exon=("+str(exonStart)+","+str(exonEnd)+") thisSeqEnd="+str(thisSeqEnd)+" nextSeqStart="+str(nextSeqStart))
								#success=False
								#break
								#now instead of giving error: fill in the sequence from ref for ref row and gaps for non-ref rows
								#print >> stderr,"Hole Between MAF blocks for transcript="+transcript+" exon=("+str(exonStart)+","+str(exonEnd)+") thisSeqEnd="+str(thisSeqEnd)+" nextSeqStart="+str(nextSeqStart)," .. fill in from ref genome"
								###here####
			
			if success: #still ok?
				toDeleteBlocks=list(toDeleteBlocks)
				toDeleteBlocks.sort()
				#now delete from toDeleteBlock from end
				for i in range(len(toDeleteBlocks)-1,-1,-1):
					toDeleteIndx=toDeleteBlocks[i]
					#print >> stderr,toDeleteIndx
					thisSeqStart=blockSeqsStarts[toDeleteIndx]
					del blockSeqs[thisSeqStart]
					del blockSeqsStarts[toDeleteIndx]
				
				
				
				#check if start and end span through the whole exon
				startOfAllSeqs=blockSeqsStarts[0]
				endOfAllSeqs=blockSeqs[blockSeqsStarts[-1]][0]
				
				if exonStart<startOfAllSeqs or exonEnd>endOfAllSeqs:
					#handle it instead of complaining and aborting
					print >> stderr,"Not Completely Covered transcript="+transcript+" exonStart="+str(exonStart)+" startOfAllSeqs="+str(startOfAllSeqs)+" exonEnd="+str(exonEnd)+" endOfAllSeqs="+str(endOfAllSeqs),"fill in seq from ref genome and gap other seqs"
					if exonStart<startOfAllSeqs:
						fillStart=exonStart
						fillEnd=startOfAllSeqs
						seqStruct=[fillEnd]+getSeqsArrayByExtractingRefSeqAndGapNonRefSeq(refGenomeBedSeqClient,genomes,chrom,fillStart,fillEnd)
						blockSeqs[fillStart]=seqStruct
					
					if exonEnd>endOfAllSeqs:
						fillStart=endOfAllSeqs
						fillEnd=exonEnd
						seqStruct=[fillEnd]+getSeqsArrayByExtractingRefSeqAndGapNonRefSeq(refGenomeBedSeqClient,genomes,chrom,fillStart,fillEnd)
						blockSeqs[fillStart]=seqStruct
						
				###########################		
					#not completel covered:
				#	Errors.append("Not Completely Covered transcript="+transcript+" exonStart="+str(exonStart)+" startOfAllSeqs="+str(startOfAllSeqs)+" exonEnd="+str(exonEnd)+" endOfAllSeqs="+str(endOfAllSeqs))
				#	success=False
				#	break		
				###########################	
				
				#update the blockSeqStarts list
				blockSeqsStarts=blockSeqs.keys()
				blockSeqsStarts.sort()
				
				#NOW loop over the blocks again and fill in gaps
				for i in range(0,len(blockSeqsStarts)):
					###here
					thisSeqStart=blockSeqsStarts[i]
					thisBlockSeqs=blockSeqs[thisSeqStart]
					thisSeqEnd=thisBlockSeqs[0]
					
					if i>0:
						if prevSeqEnd<thisSeqStart:
							#a gap here!
							print >> stderr,"Hole Between MAF blocks for transcript="+transcript+" exon=("+str(exonStart)+","+str(exonEnd)+") hole from "+str(prevSeqEnd)+" to "+str(thisSeqStart)," .. fill in from ref genome"
							
							fillStart=prevSeqEnd
							fillEnd=thisSeqStart
							seqStruct=[fillEnd]+getSeqsArrayByExtractingRefSeqAndGapNonRefSeq(refGenomeBedSeqClient,genomes,chrom,fillStart,fillEnd)
							blockSeqs[fillStart]=seqStruct	
						
					prevSeqEnd=thisSeqEnd
					
				#update the blockSeqsStarts list again							
				blockSeqsStarts=blockSeqs.keys()
				blockSeqsStarts.sort()
				
				#now we are all set for each exon and ready to stitch exons together.
								
				for i in range(len(blockSeqsStarts)-1,-1,-1):
					thisSeqStart=blockSeqsStarts[i]
					thisBlockSeqs=blockSeqs[thisSeqStart]
					
					if prevStart<0:
						#this is the last block, just add in
						
						sreq=0
						if thisSeqStart<exonStart:
							sreq=getGappedLenForUngappedK(thisBlockSeqs[1],exonStart-thisSeqStart)
							
						lreq=getGappedLenForUngappedK(thisBlockSeqs[1][sreq:],exonEnd-max(thisSeqStart,exonStart))
						
						for blockSeqString in thisBlockSeqs[1:]:
							assembledSeqs.append(blockSeqString[sreq:sreq+lreq])
					else:
						
						sreq=0
						if thisSeqStart<exonStart:
							sreq=getGappedLenForUngappedK(thisBlockSeqs[1],exonStart-thisSeqStart)	
						
						lreq=getGappedLenForUngappedK(thisBlockSeqs[1][sreq:],prevStart-max(thisSeqStart,exonStart))
									
						assIndx=0
						for blockSeqString in thisBlockSeqs[1:]:
							assembledSeqs[assIndx]=blockSeqString[sreq:sreq+lreq]+assembledSeqs[assIndx]
							assIndx+=1
							
					prevStart=thisSeqStart
				
				dummy2.append(assembledSeqs)
		
		if success:
			
		
			#now sort exonStarts
			exonStartsSorted= exonDataForTranscript.keys()
			exonStartsSorted.sort()
			
			transcriptAssembledSeqs=[]
			
			for i in range(0,len(exonStartsSorted)):
				thisExonStart=exonStartsSorted[i]
				try:
					thisAssembledSeqs=exonDataForTranscript[thisExonStart][2]
				except: #out of bound, not assembled
					Errors.append("OutOfBound transcript="+transcript+" start="+str(thisExonStart))
					success=False
					break
				
				if i==0: #first exon
					for thisAssembledSeq in thisAssembledSeqs:
						transcriptAssembledSeqs.append(thisAssembledSeq)
				else:
					for i in range(0,len(thisAssembledSeqs)):
						transcriptAssembledSeqs[i]+=thisAssembledSeqs[i]
					
			#now for strand
			if strand=='-':
				#reverse complement!~
				for i in range(0,len(transcriptAssembledSeqs)):
					transcriptAssembledSeqs[i]=reverse_complement(transcriptAssembledSeqs[i])
		
			assembledTranscriptStart=exonStartsSorted[0]
			#print >> stderr,exonDataForTranscript[exonStartsSorted[-1]]
			assembledTranscriptEnd=exonDataForTranscript[exonStartsSorted[-1]][1]
			
			if assembledTranscriptStart!=transcriptStart:
				success=False
				Errors.append("assembled transcript start != transcript Start for transcript="+transcript+" assembledstart="+str(assembledTranscriptStart)+" transcriptStart="+str(transcriptStart));
			
			if assembledTranscriptEnd!=transcriptEnd:
				success=False
				Errors.append("assembled transcript end != transcript end for transcript="+transcript+" assembledend="+str(assembledTranscriptEnd)+" transcriptEnd="+str(transcriptEnd));
				
			
		if success:
			print >> stdout,"\t".join([transcript]+transcriptAssembledSeqs)
		else:
			print >> stderr,"assembly of transcript",transcript,"failed"
			for error in Errors:
				print >> stderr,"\t"+error
				
	refGenomeBedSeqClient.close()
			