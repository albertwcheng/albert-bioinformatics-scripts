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

### splitlines.py line#,...  files,...
from sys import stderr, stdout, exit
import sys
from albertcommon import *

def splitlines_Main(srcFile,lines,dstFiles):
	
	llines=len(lines)
	if len(dstFiles)<len(lines):
		print >> stderr, "number of destination files is smaller than the number of partitions"
		exit()
	
	if len(dstFiles)>len(lines)+1:
		print >> stderr, "number of destination files is larger than the number of partitions + 1"
		exit()
	elif len(dstFiles)==len(lines)+1:
		print >> stderr, "number of destination files = number of partitions + 1. All the remaining lines after all partitions are written to the last destination file"
		lines.append(-1) #a negative number such that it will not reach 0 by decrementing
	
	fin=generic_istream(srcFile)
	
	lino=0
	
	linei=0
	
	curFout=open(dstFiles[linei],"w")

	for line in fin:
		lino+=1
		if lines[linei]==0:
			curFout.close()
			if linei==llines:
				print >> stderr,"warning: not all the lines in src file are outputed"
				break
			else:
				linei+=1
				curFout=open(dstFiles[linei],"w")
		
		curFout.write(line)
		lines[linei]-=1
	
	
	curFout.close()	
	fin.close()
	
	print >> stderr,lino,"lines of source file processed"
	
	if linei<llines and lines[linei]>0:
		print >> stderr,"last file does not contain the row specified by its partition"
	
	if linei<llines-1:
		print >> stderr,"source file finished before running through all partitions, some destination files are not written"
	
def usageExit(programName):
	print >> stderr,"Usage:",programName,"sourceFile lines,... destFile,..."
	exit()
	
if len(sys.argv)!=4:
	usageExit(sys.argv[0])
	
srcFile,linesStr,dstFiles=sys.argv[1:]

lines=[]
for s in linesStr.split(","):
	lin=int(s)
	if lin<1:
		print >> stderr, "invalid partition size",lin
		usageExit(sys.argv[0])
	lines.append(lin)

dstFiles=dstFiles.split(",")

splitlines_Main(srcFile,lines,dstFiles)