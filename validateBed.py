#!/usr/bin/env python

from sys import *
from getopt import getopt

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] bedfile chrSizeList > validatedBedFile 2> validationError"
	print >> stderr,"Options:"
	print >> stderr,"--trim-off-bound. Trim the off bound coordinates"
	print >> stderr,"--fs x. Set the separator used in the bed file"
	print >> stderr,"--remove-entries-not-in-chr-list. Remove those entries where chromosome is not in the list"
	print >> stderr,"--remove-non-bed-entries. Output non bed entries without processing"
	print >> stderr,"--remove-invalid-bound. After trimming (if --trim-off-bound is set), remove bounds where start0 >= end1 or off-bound"
	print >> stderr,"--off-stderr. turn off stderr reporting"
	exit()
	
def loadChrSizes(filename):
	chrSizes=dict()
	fil=open(filename)
	for lin in fil:
		fields=lin.rstrip("\r\n").split("\t")
		chrSizes[fields[0]]=int(fields[1])
	
	fil.close()
	return chrSizes

def outputBedAndError(lino,fields,fs,msg,outputFields,offStderr):
	if outputFields:
		print >> stdout,fs.join(fields)
	
	if not offStderr and len(msg)>0:
		print >> stderr,"line",lino,":",";".join(msg),"" if outputFields else "skipped in output"
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['trim-off-bound','remove-invalid-bound','fs=','remove-entries-not-in-chr-list','remove-non-bed-entries','off-stderr'])
	
	try:
		bedfile,chrSizeFile=args
	except:
		printUsageAndExit(programName)
	
	removeOffBound=False
	trimOffBound=False
	removeEntriesNotInChrList=False
	removeNonBedEntries=False
	fs="\t"
	offStderr=False
	
	for o,v in opts:
		if o=='--trim-off-bound':
			trimOffBound=True
		elif o=='--trim-off-bound':
			trimOffBound=True
		elif o=='--remove-invalid-bound':
			removeInvalidBound=True
		elif o=='--fs':
			fs=v
		elif o=='--remove-entries-not-in-chr-list':
			removeEntriesNotInChrList=True
		elif o=='--remove-non-bed-entries':
			removeNonBedEntries=True
		elif o=='--off-stderr':
			offStderr=True
	
	chrSizes=loadChrSizes(chrSizeFile)
	
	#now open bedFile
	fil=open(bedfile)
	lino=0
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		
		fields=lin.split(fs)
		outputFields=True
		msg=[]
		
		if len(fields)<3:
			msg.append("non BED entry")
			if removeNonBedEntries:
				outputFields=False
			
			outputBedAndError(lino,fields,fs,msg,outputFields,offStderr) #not going further but depends on wether to output non bed entries, print or not
			continue #has to discontinue
		else:
			try:
				chrom,start0,end1=fields[0:3]
				start0=int(start0)
				end1=int(end1)
			except:
				#if this fail means either start0 is not number or end1 is not number
				#so not a bed entry
				msg.append("non BED entry"	)
				if removeNonBedEntries:
					outputFields=False
				outputBedAndError(lino,fields,fs,msg,outputFields,offStderr) #not going further but depends on wether to output non bed entries, print or not
				continue  #has to discontinue
			
			if start0<0:
				msg.append("start0<0")
				if trimOffBound:
					start0=0
					fields[1]=str(start0)
					msg.append("start0 trimmed to zero")
			
			
			try:
				thisChrSize=chrSizes[chrom]
			except KeyError:
				msg.append("chrom",chrom,"not found in chr size list")
				if removeEntriesNotInChrList: #this is to be skipped anyway
					outputBedAndError(lino,fields,fs,msg,False,offStderr)
					continue #discont
				else:
					msg.append("proceed without bounding on chr Size by assuming a super big chrom size")
					thisChrSize=100000000000
			
			if end1<=start0:
				msg.append("end1<=start0")
				if removeInvalidBound: 
					outputFields=False
				outputBedAndError(lino,fields,fs,msg,outputFields,offStderr)
				continue  #no way to repair discont
			
			if start0>=thisChrSize-1:
				msg.append("start0 "+str(start0)+" >= "+str(thisChrSize-1)+" size of chrom-1")
				if removeInvalidBound: 
					outputFields=False
				outputBedAndError(lino,fields,fs,msg,outputFields,offStderr)
				continue  #no way to repair discont
					
			if end1>thisChrSize:
				msg.append("end1> "+str(end1)+" > "+str(thisChrSize)+" size of chrom")
				if trimOffBound:
					end1=thisChrSize
					fields[2]=str(end1)
					msg.append("end1 trimmed to chr size="+str(thisChrSize))
			

			#now can we still output?
			if (start0>=0 and start0<end1 and end1<=thisChrSize) or not removeInvalidBound:
				#we are happy
				outputBedAndError(lino,fields,fs,msg,True,offStderr)
			else:
				outputBedAndError(lino,fields,fs,msg,False,offStderr)
		
	fil.close()