#!/usr/bin/python

from sys import *

def output(seqname,seq):
	if len(seq)>0:
		print >> stdout,seqname+"\t"+seq

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		print >> stderr,programName,"in.fa > out.seq"
		exit()
		
	fil=open(filename)
	seqname=""
	seq=""
	for lin in fil:
		lin=lin.strip()
		if len(lin)==0:
			continue
		
		if lin[0]=='>':
			output(seqname,seq)
			seq=""
			seqname=lin
		else:
			seq+=lin
		
	fil.close()
	
	output(seqname,seq)