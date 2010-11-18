#!/usr/bin/python

#removeInvalidCharactersFromSeq.py

from sys import *
from getopt import getopt

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['cap-seq-off','remove-zero-length-seq','split-off'])
	
	capSeq=True
	removeZeroLen=False
	splitOff=False
	
	try:
		filename,charset=args
	except:
		print >> stderr,programName,"filename charset[e.g., ACGT]"
		print >> stderr,"automatically also capSeq [turn off by --cap-seq-off: remove all lowercase letters]"
		print >> stderr,"--remove-zero-length-seq"
		print >> stderr,"--split-off ,splitoff sequences interrupted by unknown sequence"
		exit()
	
	for o,v in opts:
		if o=='--cap-seq-off':
			capSeq=False
		elif o=='--remove-zero-length-seq':
			removeZeroLen=True
		elif o=='--split-off':
			splitOff=True
	
	
	fil=open(filename)
	for lin in fil:
		fields=lin.strip().split("\t")
		seq=fields[1]
		fields[1]=""
		if capSeq:
			seq=seq.upper()
		
		lastIsSplitter=True
		for s in seq:
			if s in charset:
				fields[1]+=s
				lastIsSplitter=False
			elif splitOff:
				if not lastIsSplitter:
					fields[1]+='|'
				lastIsSplitter=True
		
		if splitOff:
			seqsplits=fields[1].split("|")
			splitI=0
			for seqsplit in seqsplits:
				if len(seqsplit)==0:
					continue
				splitI+=1
				print >> stdout,fields[0]+"|"+str(splitI)+"\t"+seqsplit #
			
		else:		
			if removeZeroLen and len(fields[1])==0:
				continue
			
			print >> stdout,"\t".join(fields)
	
	fil.close()