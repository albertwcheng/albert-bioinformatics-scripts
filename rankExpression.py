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
#rank expression

import sys
from albertcommon import *
from getopt import getopt


programName=sys.argv[0]

opts,args=getopt(sys.argv[1:],'',['output-cdt','output-changevector=','output-colorvector=','output-rankvector'])

outputCDT=False
outputChangeVector=False
outputChangeVectorScale=0
outputColorVector=False
outputColorVectorScale=0
outputRankVector=False
for o,v in opts:
	if o=="--output-cdt":
		outputCDT=True
	elif o=="--output-changevector":
		outputChangeVector=True
		outputChangeVectorScale=float(v)
	elif o=="--output-colorvector":
		outputColorVector=True
		outputColorVectorScale=float(v)
	elif o=="--output-rankvector":
		outputRankVector=True



headerRow=1
separator="\t"

try:
	filename,colString=args
except ValueError:
	print >> sys.stderr,"Usage:",programName,"filename [--output-cdt --output-changevector --output-colorvector --output-rankvector] -valueCol[+=all but first col]"
	sys.exit()

startRow=headerRow+1
header,prestarts=getHeader(filename,headerRow,startRow,separator)

if colString=="+":
	valueCols=range(1,len(header))
else:
	valueCols=getCol0ListFromCol1ListStringAdv(header,colString)

def colorVector(L):
	cv=[]
	for x in L:
		if x<0:
			cv.append(-1)
		elif x>0:
			cv.append(1)
		else:
			cv.append(0)

	return cv

def changeVector(L):
	cv=[]
	for i in range(1,len(L)):
		if L[i]>L[i-1]:
			cv.append(1)
		elif L[i]<L[i-1]:
			cv.append(-1)
		else:
			cv.append(0)

	return cv

def realChangeVector(L):
	cv=[]
	for i in range(1,len(L)):
		cv.append(L[i]-L[i-1])


	return cv

def itemsAt(L,LI):
	L2=[]
	for li in LI:
		L2.append(L[li])

	return L2

def suffixStrVector(L,suffix):
	LC=L[:]	
	for i in range(0,len(L)):
		LC[i]+=suffix
	return LC

def firstFieldVectorComparator(X,Y):
	return vectorComparator(X[0],Y[0])

fil=open(filename)
lino=0
VALUES=[]

headerSelected=itemsAt(header,valueCols)


def mean(L):
	return float(sum(L))/len(L)

for lin in fil:
	lino+=1
	if lino<startRow:
		continue
	
	lin=lin.rstrip("\r\n")
	fields=lin.split(separator)
	values=StrListToFloatList(itemsAt(fields,valueCols))
	CoV=colorVector(values)
	ChV=changeVector(values)
	RkV=rank(values,True)
	rChV=realChangeVector(values)
	sortVector=CoV+ChV+RkV+values #added +values
	#sortVector=CoV+rChV+values #+ChV+RkV
	
	rejoinFields=False

	if outputCDT:	
		fields.insert(1,fields[0])
		rejoinFields=True
	
	if outputChangeVector:
		fields.extend(["0"]+toStrList(multiplyVector(ChV,outputChangeVectorScale)))
		rejoinFields=True

	if outputColorVector:
		fields.extend(toStrList(multiplyVector(CoV,outputColorVectorScale)))
		rejoinFields=True

	if outputRankVector:
		fields.extend(toStrList(RkV))
		rejoinFields=True
	
	if rejoinFields:
		lin=separator.join(fields)

	
	VALUES.append([sortVector,lin])

VALUES.sort(firstFieldVectorComparator)
VALUES.reverse()
linoout=0
for prestart in prestarts: 
	linoout+=1
	if outputCDT:
		if linoout==1:
			prestart.insert(1,"NAME")
		else:
			prestart.insert(1,"1")

	if outputChangeVector:
		prestart.extend(suffixStrVector(headerSelected,"_Change"))

	if outputColorVector:
		prestart.extend(suffixStrVector(headerSelected,"_Color"))

	if outputRankVector:
		prestart.extend(suffixStrVector(headerSelected,"_Rank"))


	print >> sys.stdout,separator.join(prestart)

for value in VALUES:
	linoout+=1
	print >> sys.stdout,value[1]
	print >> sys.stderr,value[0],value[1]

fil.close()
