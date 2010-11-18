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

from sys import *

def readFastaIntoSeqArray(filename):
	seqs=[]
	fil=open(filename)
	curSeq=""
	for lin in fil:
		lin=lin.strip()
		if lin[0]==">":
			if curSeq!="":
				seqs.append(curSeq)			
			curSeq=""
		else :
			curSeq+=lin.upper()

		

	fil.close()
	return seqs

def similateAllReadsFromSeq(seq,readLength,dst):
	for i in range(0,len(seq)-readLength+1):
		dst.append(seq[i:i+readLength])

def similateAllReads(seqs,readLength):
	reads=[]	
	for seq in seqs:
		similateAllReadsFromSeq(seq,readLength,reads)

	return reads


def complement(c):
	if c=="A":
		return "T"
	
	if c=="T":
		return "A"

	if c=="a":
		return "t"

	if c=="t":
		return "a"

	if c=="C":
		return "G"
	
	if c=="c":
		return "g"

	if c=="G":
		return "C"
	
	if c=="g":
		return "c"

	if c=="u":
		return "a"

	if c=="U":
		return "A"

	return c

def reverseComplement(seq):
	rc=""
	for i in range(len(seq)-1,-1,-1):
		c=seq[i]
		rc+=complement(c)

	return rc
		

def printUsageAndExit(programName):
	print >> stderr,programName,"readlength reffile(fasta) readfiles(fastq) "
	print >> stderr, "this program reads in ref file, parse into reads, for each of fastq file, output the seq if it is matched with a simulated read"
	exit()

if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	try:
		readlength=int(args[0])
		reffile=args[1]
		readfiles=args[2:]
	except:
		printUsageAndExit(programName)	
	print >> stderr, "arguments received:",argv
	print >> stderr,"reading ref seqs from",reffile
	refseqs=readFastaIntoSeqArray(reffile)
	print >> stderr,"simulating reads from ref seqs"
	simRefReads=similateAllReads(refseqs,readlength)
	
	print >> stderr,"total ref reads:",len(simRefReads)
	simRefReads=list(set(simRefReads))
	print >> stderr,"total uniq ref reads:",len(simRefReads)
	for readfile in readfiles:
		print >> stderr,"loading fastq reads from",readfile
			
		numSeq=0
		
		fil=open(readfile)
		readNext=False
		for lin in fil:
			lin=lin.strip()
			if lin[0]=='+':
				readNext=True
			elif readNext:
				seq=lin.upper()
				numSeq+=1
				if numSeq%100000==1:
					print >> stderr,"processed read no",numSeq
				rcSeq=reverseComplement(seq)
				if seq in simRefReads: 				
					print >> stdout, seq+"\t"+"+"
				elif rcSeq in simRefReads:
					print >> stdout, seq+"\t"+"-"
				
				readNext=False	

		fil.close()
		print >> stderr,"total fastq reads processed:",numSeq

			

