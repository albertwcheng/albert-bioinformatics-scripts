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

COMPL={'A':'T',
	   'T':'A',
	   'C':'G',
	   'G':'C',
	   'U':'A',
	   'a':'t',
	   't':'a',
	   'u':'a',
	   'c':'g',
	   'g':'c'}

def complement(b):
	global COMPL
	try:
		return COMPL[b]
	except:
		return b

def reverseComplement(s):
	rc=""
	for b in s:
		rc=complement(b)+rc
		
	return rc

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,col=args
	except:
		print >> stderr,programName,"filename col"
		exit()
		
	col=int(col)-1
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
		if len(fields)<col+1:
			print >> stderr,"not enough fields for line",lino,fields,":ignored"
			continue
		
		fields.append(reverseComplement(fields[col]))
		print >> stdout,"\t".join(fields)
	
	fil.close()
	