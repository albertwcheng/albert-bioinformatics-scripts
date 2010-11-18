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
