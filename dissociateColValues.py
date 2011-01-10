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
from albertcommon import *
from getopt import *


def printUsageAndExit(programName):
	print >> stderr,programName,"<-i<internal-separator> -s<colSelector> > .... [-d col-delimiter] [other options, see below] filename > outfile"
	print >> stderr,"-u only unique items"
	print >> stderr,"--startRow set startrow"
	print >> stderr,"--headerRow set headerrow"
	print >> stderr,"--roll-over roll the list instead of multiplying. i.e., 1,2,3 a,b,c +,- will become 1 a + <return> 2 b - <return> 3 c + <return>"
	explainColumns(stderr)
	exit()

def rolloverCombinations(fields):
	lfields=[]
	
	numCols=len(fields)
	
	for field in fields:
		lfields.append(len(field))
	
	roComb=[]
	
	maxLFields=max(lfields) #there should then be maxLFields lines
	for i in range(0,maxLFields):
		newComb=[]
		roComb.append(newComb)
		for lthisfield,thisField in zip(lfields,fields):
			ia= i % lthisfield
			newComb.append(thisField[ia])
		
	return roComb


if __name__=='__main__':




	programName=argv[0]
	opt,args=getopt(argv[1:],'i:s:d:u',['startRow=','headerRow=','roll-over'])
	try:
		filename,=args
	except:
		printUsageAndExit(programName)

	internalSeparator="|"
	
	colSelectors=[]
	internalSeparators=[]
	
	rollover=False
	fs="\t"
	headerRow=-1
	startRow=-1
	uniq=False

	for o,v in opt:
		if o=='-i':
			internalSeparator=v
		elif o=='-s':
			colSelectors.append(v)
			internalSeparators.append(internalSeparator)
		elif o=='-d':
			fs=v
		elif o=='-u':
			uniq=True
		elif o=='--startRow':
			startRow=int(v)
		elif o=='--headerRow':
			headerRow=int(v)
		elif o=='--roll-over':
			rollover=True

	if startRow ==-1 and headerRow==-1:
		startRow=2

	if headerRow==-1:
		headerRow=startRow-1
	
	if startRow==-1:
		startRow=headerRow+1
	

	startRow=headerRow+1
	header,prestarts=getHeader(filename,headerRow,startRow,fs)

	for i in range(0,len(colSelectors)):
		colSelectors[i]=getCol0ListFromCol1ListStringAdv(header,colSelectors[i])

	#now expand
	
	
	
	fil=open(filename)
	lino=0
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		if lino<startRow:
			print >> stdout,lin
			continue

		fields=lin.split(fs)
		
		for i in range(0,len(fields)):
			fields[i]=[fields[i]]

		for colSelector,internalSeparator in zip(colSelectors,internalSeparators):
			for col in colSelector:
				newFieldItems=[]
				for fieldItem in fields[col]:
					newFieldItems.extend(fieldItem.split(internalSeparator))
				if uniq:
					fields[col]=list(set(newFieldItems))
				else:
					fields[col]=newFieldItems

		if rollover:
			lineCombinations=rolloverCombinations(fields)
		else:
			lineCombinations=findAllCombinations(fields)

		for linCom in lineCombinations:
			print >> stdout,fs.join(linCom)		
				
		
	fil.close()

