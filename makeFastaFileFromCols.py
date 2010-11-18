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

from albertcommon import *
from getopt import getopt
from sys import stderr,stdout,argv

def usageExit(programName):
	print >> stderr, "Usage:",programName,"filename fastaheadercols sequencecols"
	print >> stderr, "Options:"
	print >> stderr, "-F,-t,-d,--fs string input separator string"
	print >> stderr, "-r,--headerRow row set the header row"
	print >> stderr, "--ignore-empty-header --ignore-empty-sequence --header-joiner joiner --sequence-joiner joiner --auto-header pref"
	explainColumns(stderr)	
	exit()




if __name__=="__main__":
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:',['fs=','headerRow=','ignore-empty-header','auto-header=','ignore-empty-sequence','header-joiner=','sequence-joiner='])


	headerRow=1
	headerJoiner="_"
	sequenceJoiner="_"
	ignoreEmptyHeader=False
	autoHeaderPrefix=""
	autoHeader=False;
	ignoreEmptySequence=True
	fs="\t"

	

	try:
		fileName,fastaheadercols,sequencecols=args
	
		for a,v in optlist:
			if a in ["-F","-t","-d","--fs"]:
				fs=replaceSpecialChar(v)
			elif a in ["-r","--headerRow"]:
				headerRow=int(v)
			elif a in ["--ignore-empty-header"]:
				ignoreEmptyHeader=True
			elif a in ["--ignore-empty-sequence"]:
				ignoreEmptySequence=True
			elif a in ["--auto-header"]:
				autoHeaderPrefix=v
				autoHeader=True
			elif a in ["--header-joiner"]:
				headerJoiner=v
			elif a in ["--sequence-joiner"]:
				sequenceJoiner=v
			

		startRow=headerRow+1
		#headerRow-=1
		header,prestarts=getHeader(fileName,headerRow,startRow,fs)
		
		
		fastaheadercols=getCol0ListFromCol1ListStringAdv(header,fastaheadercols)
		sequencecols=getCol0ListFromCol1ListStringAdv(header,sequencecols)
	except ValueError:
		usageExit(programName)
			
	
	
	fin=open(fileName)
	lino=0
	entryIndex=1
	for lin in fin:
		lino+=1
		if lino<startRow:
			continue
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		sequence=sequenceJoiner.join(selectListByIndexVector(fields,sequencecols)).replace(" ","")	
		fastaheader=headerJoiner.join(selectListByIndexVector(fields,fastaheadercols))
		if ignoreEmptySequence and len(sequence)==0:
			continue			

		if autoHeader:
			midstr=""
			if len(fastaheader)>0:
				midstr=headerJoiner
			if len(autoHeaderPrefix)>0:
				fastaheader+=midstr+autoHeaderPrefix+fastaJoiner+str(entryIndex)
			else:
				fastaheader+=midstr+str(entryIndex)

		if ignoreEmptyHeader and len(fastaheader)==0:
			continue

		print >> stdout,">"+fastaheader
		print >> stdout,sequence
		entryIndex+=1


	fin.close()
		
		
