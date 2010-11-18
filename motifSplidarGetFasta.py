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
#extract sequence file

from albertcommon import *
from sys import *
import sys


def printUsageAndExit(programName):
	print >> stderr,programName,"filename seqcols"
	exit()


headerRow=1
startRow=2
fs="\t"
programName=argv[0]
args=argv[1:]

try:
	filename,seqcols=args
except:
	printUsageAndExit(programName)


header,prestart=getHeader(filename,headerRow,headerRow,fs)
seqcols=getCol0ListFromCol1ListStringAdv(header,seqcols)

headerName=getSubvector(header,seqcols)


ofiles=dict()
lino=0
fil=open(filename)
for lin in fil:
	lino+=1
	lin=lin.rstrip("\r\n")
	if lino<startRow:
		continue
	fields=lin.split(fs)
	for headernam,seqcol in zip(headerName,seqcols):
		seqraw=fields[seqcol]
		seqsp=seqraw.split("|")
		if len(seqsp)==0:
			continue
		for seqs in seqsp:
			seqs=seqs.strip()
			if len(seqs)==0:
				continue
			elementname=seqs[0:2]

			seq=seqs[2:len(seqs)]
			oprefix=headernam+"."+elementname
			ofilename=oprefix+".fa"
			if ofilename not in ofiles:
				fout=open(ofilename,"w")
				ofil=[fout,0]
				ofiles[ofilename]=ofil
			
			else:
				ofil=ofiles[ofilename]
		
		
			ofil[1]+=1
			print >> ofil[0],">"+oprefix+"_"+str(ofil[1])
			print >> ofil[0],seq

fil.close()

#close files
for ofilename,ofil in ofiles.items():
	ofil[0].close()




