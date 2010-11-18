#!/usr/bin/env python


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
