#!/usr/bin/env python

'''

find argmax(pvalue){FDR(pvalue)<FDRCutOff}

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
from albertcommon import *

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	headerRow=1
	startRow=2	
	fs="\t"

	try:
		filename,pvalueCol,FDRCol,FDRCutOff=args
	except:
		print >> stderr,programName,"filename pvalueCol FDRCol FDRCutOff"
		explainColumns(stderr)
		exit()


	header,prestarts=getHeader(filename,headerRow,startRow,fs)
		
	pvalueCol=getCol0ListFromCol1ListStringAdv(header,pvalueCol)[0]
	FDRCol=getCol0ListFromCol1ListStringAdv(header,FDRCol)[0]	

	lines=[]
	pvalues=[]

	maxpvalue=-10000.00

	fil=open(filename)
	lino=0	

	#first pass
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		if lino<startRow:
			continue

		pvalue=float(fields[pvalueCol])
		FDR=float(fields[FDRCol])
	
		if FDR<=FDRCutOff:
			maxpvalue=max(maxpvalue,pvalue)	
		
		
	fil.close()

	print >> stderr,"FDRCutOff="+str(FDRCutOff)
	print >> stderr,"maxpvalue="+str(maxpvalue)
	
	#second pass	
	fil=open(filename)
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if lino<startRow:
			print >> stdout,lin
			continue

		fields=lin.split(fs)
		pvalue=float(fields[pvalueCol])
		
		if pvalue<=minpvalue:
			print >> stdout,lin	

	fil.close()


