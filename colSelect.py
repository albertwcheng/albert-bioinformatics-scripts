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

from sys import stderr,stdout,argv, exit
from albertcommon import *
from getopt import getopt
from colStat import *

def usageExit(programName):
	print >> stderr, "Usage:",programName,"filename colSelector"
	print >> stderr, "Options:"
	print >> stderr, "-F,-t,-d,--fs string input separator string"
	print >> stderr, "-o,--ofs string   output separator string"
	print >> stderr, "-s,--sort sort the coordinate. Default no sorting"
	print >> stderr, "-r,--headerRow row set the header row"
	print >> stderr, "-f,--format format: [col1] col0 name excel"
	explainColumns(stderr)	
	exit()

if __name__=="__main__":
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:s:o:',['ofs=','fs=','headerRow=','format=','sort'])

	sort=False
	headerRow=1
	ofs=" "
	fs="\t"
	format="col1"
	formats=["col0","col1","excel","name"]
	
	if len(args)!=2:
		usageExit(programName)
	else:
		fileName,colString=args
	
		for a,v in optlist:
			if a in ["-F","-t","-d","--fs"]:
				fs=replaceSpecialChar(v)
			elif a in ["-o","--ofs"]:
				ofs=replaceSpecialChar(v)
			elif a in ["-r","--headerRow"]:
				headerRow=int(v)
			elif a in ["-f","--format"]:
				format=v
				if format not in formats:
					print >> stderr,"Error: format",format,"not found"
					usageExit(programName)
			elif a in ["-s","--sort"]:
				sort=True

		startRow=headerRow+1
		#headerRow-=1
		header,prestarts=getHeader(fileName,headerRow,startRow,fs)
		
		idCols=getCol0ListFromCol1ListStringAdv(header,colString)
		
		if sort:
			idCols.sort()
		
		outputs=[]
		
		
		for id0 in idCols:
			if format=="col0":
				outputs.append(str(id0))
			elif format=="col1":
				outputs.append(str(id0+1))
			elif format=="name":
				outputs.append(header[id0])
			elif format=="excel":
				outputs.append(excelColIndex(id0))
		
		print >> stdout, ofs.join(outputs)

