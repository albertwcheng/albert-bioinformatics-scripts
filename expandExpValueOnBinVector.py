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
from sys import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] filename idCol binVectorCols valueCols > output"
	print >> stderr,"Options:"
	#['want-m1','ommit-0','ommit-1','ommit-spec=','start-row','header-row','fs','print-rows-with-only-NA','swing-to-col']
	print >> stderr,"--want-m1   use wildcast set"
	print >> stderr,"--ommit-0   ommit all rows with a 0 in the binary vector"
	print >> stderr,"--ommit-1   ommit all rows with a 1 in the binary vector"
	print >> stderr,"--ommit-spec  i,j,k,l,... ommit a particular binary vector pattern"
	print >> stderr,"--start-row r [default:2] set start row"
	print >> stderr,"--header-row r [default:1] set header row"
	print >> stderr,"--fs s [default: TAB] set fields separator"
	print >> stderr,"--print-rows-with-only-NA   print also rows with only NA values"
	print >> stderr,"--swing-to-col  represent all value cols as one col, and append to rows (geneid+valuelabel) per cols."
	print >> stderr,"--order-pattern-first  order pattern -> value [default: order value -> pattern ]"
	print >> stderr,"--no-combination  do not produce combinatorial patterns"
	print >> stderr,"--include-spec i,j,k,l,.... add a particular binary vector pattern"
	exit()


def toIntArray(L):
	I=[]
	for s in L:
		try:
			x=int(s)
		except ValueError:
			x=int(float(s))

		I.append(x)

	return I

def generateM1Patterns(binv):
	if len(binv)<1:
		return []

	tmp=[(binv[0],),(-1,)]
	for i in range(1,len(binv)): #grow
		thisTmp=[]
		for t in tmp:
			thisTmp.append(t+(binv[i],))
			thisTmp.append(t+(-1,))
		tmp=thisTmp

	return tmp

def ommitPatternsWith(L,x):
	L1=[]
	for t in L:
		if x not in t:
			L1.append(t)

	return L1

def ommitPatterns(L,p):
	L1=[]
	for t in L:
		if t!=p:
			L1.append(t)

	return L1

def IsPatternMatched(key,target):
	for k,t in zip(key,target):
		if k!=-1 and k!=t: #-1 is masked
			return False
	return True	

def getLabelByBinVector(header,cols,pattern):
	labelons=[]	
	for c,p in zip(cols,pattern):
		if p==0:
			labelons.append("~"+header[c])
		elif p==1:
			labelons.append(header[c])

	return labelons

def numOfClasses(pattern):
	num_m1=0
	num_0=0
	num_1=0
	for p in pattern:
		if p==1:
			num_1+=1
		elif p==0:
			num_0+=1
		elif p==-1:
			num_m1+=1
		else:
			print >> stderr,"fatal error: unknown pattern code",p,"of",pattern

	return (num_m1,num_0,num_1)

def deb():
	print generateM1Patterns((1,0,1,0))

if __name__=="__main__":

	#deb()

	#exit() 

	programName=argv[0]
	opt,args=getopt(argv[1:],'',['want-m1','ommit-0','ommit-1','ommit-spec=','start-row','header-row','fs','print-rows-with-only-NA','swing-to-col','order-pattern-first','no-combination','include-spec='])
	
	orderPatternFirst=False
	swingValuesToCol=False
	want_m1=False
	ommit_0=False
	ommit_1=False
	ommit_spec=[]
	no_combination=False
	include_spec=[]
	labelj="_"
	fillNA="NA"
	startRow=-1
	headerRow=-1
	fs="\t"
	printRowsWithOnlyNA=False

	for o,v in opt:
		if o=='--want-m1':
			want_m1=True	
		elif o=='--ommit-0':
			ommit_0=True
		elif o=='--ommit-1':
			ommit_1=True
		elif o=='--ommit-spec':
			ommit-spec.append(tuple(toIntArray(v.split(","))))
		elif o=='--start-row':
			startRow=int(v)
		elif o=='--header-row':
			headerRow=int(v)
		elif o=='--print-rows-with-only-NA':
			printRowsWithOnlyNA=True	
		elif o=='--swing-to-col':
			swingValuesToCol=True
		elif o=='--order-pattern-first':
			orderPatternFirst=True
		elif o=='--no-combination':
			no_combination=True
		elif o=='--include-spec':
			include_spec.append(tuple(toIntArray(v.split(","))))
	try:
		filename,idCol,binVectorCols,valueCols=args
	except:
		printUsageAndExit(programName)


	#now the real deal

	if startRow==-1:
		if headerRow==-1:
			startRow=2
			headerRow=1
		else:
			startRow=headerRow+1
	else:
		if headerRow==-1:
			headerRow=startRow-1
		
	header,prestarts=getHeader(filename,headerRow,startRow,fs)	
	
	idCol=getCol0ListFromCol1ListStringAdv(header,idCol)[0]
	binVectorCols=getCol0ListFromCol1ListStringAdv(header,binVectorCols)
	valueCols=getCol0ListFromCol1ListStringAdv(header,valueCols)

	idLabel=header[idCol]
	binVectorLabels=getSubvector(header,binVectorCols)
	valueColLabels=getSubvector(header,valueCols)

	#now read file and generate pattern dictionary on the binary vector cols (first pass)
	
	patternSet=set()

	fil=open(filename)
	lino=0	
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		fields=lin.rstrip().split(fs)
		thisPattern=tuple(toIntArray(getSubvector(fields,binVectorCols)))
		patternSet.add(thisPattern)

	fil.close()
	
	patternSet=list(patternSet)
	
	if want_m1:
		patternSetNew=set(patternSet[:])
		for pattern in patternSet:
			m1pattern=generateM1Patterns(pattern)
			for m1p in m1pattern:
				patternSetNew.add(m1p)
		patternSet=list(patternSetNew)

	if ommit_0:
		patternSet=ommitPatternsWith(patternSet,0)
	
	if ommit_1:
		patternSet=ommitPatternsWith(patternSet,1)

		
	if no_combination:
		if not want_m1:
			print >> stderr,"no-combination flag on without want-m1"
			exit()

		patternSetNew=[]
		for pattern in patternSet:
			num_m1,num_0,num_1=numOfClasses(pattern)
			if num_1<=1 and num_0<1:
				patternSetNew.append(pattern)
			

		patternSet=patternSetNew
	
	if len(ommit_spec)>0:
		patternSetNew=[]
		for pattern in patternSet:
			if pattern not in ommit_spec:
				patternSetNew.append(pattern)

		patternSet=patternSetNew

	if len(include_spec)>0:
		for pattern in include_spec:
			if pattern not in patternSet:
				patternSet.append(pattern)
		
	#now we have our pattern library defined well
	
	patternDict=dict()
	for pattern in patternSet:
		
		patternDict[pattern]=getLabelByBinVector(header,binVectorCols,pattern)	
		print >> stderr,"output",pattern,"as label",patternDict[pattern]	

	#second pass

	patternSet.sort()

	fil=open(filename)
	
	lino=0
	for lin in fil:

		

		lino+=1

		fields=lin.rstrip().split(fs)

		outFields=[fields[idCol]]
		

		

		if lino<startRow:
			#print >> stderr,patternDict
			if swingValuesToCol:
				for pattern in patternSet:
					patternL=patternDict[pattern]
					if len(patternL)==0:
						colLabel="*"
					else:
						colLabel=labelj.join(patternL)
					
					outFields.append(colLabel)
				
			else:
				#for each value combination and each pattern pattern

				if orderPatternFirst:
					for pattern in patternSet:					
						for valColLabel,valueCol in zip(valueColLabels,valueCols):
							patternL=patternDict[pattern]
							if len(patternL)==0:
								colLabel=valColLabel
							else:
								colLabel=labelj.join(patternDict[pattern])+labelj+valColLabel
							print >> stderr,"output field header",colLabel,"for",pattern
							outFields.append(colLabel)

				else:
					for valColLabel,valueCol in zip(valueColLabels,valueCols):
						for pattern in patternSet:
							patternL=patternDict[pattern]
							if len(patternL)==0:
								colLabel=valColLabel
							else:
								colLabel=valColLabel+labelj+labelj.join(patternDict[pattern])
							print >> stderr,"output field header",colLabel,"for",pattern
							outFields.append(colLabel)
			#print >> stderr,outFields
			print >> stdout,fs.join(outFields)		
		else:
			thisPattern=tuple(toIntArray(getSubvector(fields,binVectorCols)))
			printOut=False

			if swingValuesToCol:
				for valColLabel,valueCol in zip(valueColLabels,valueCols):
					#swing!
					outFields=[fields[idCol]+labelj+valColLabel]
					for pattern in patternSet:
						if IsPatternMatched(pattern,thisPattern):
							printOut=True
							outFields.append(fields[valueCol])
						else:
							outFields.append(fillNA)

					if printOut or printRowsWithOnlyNA:
						print >> stdout,fs.join(outFields)
		
				
			else:
				if orderPatternFirst:
					for pattern in patternSet:
						for valueCol in valueCols:
							if IsPatternMatched(pattern,thisPattern):
								printOut=True
								outFields.append(fields[valueCol])
							else:
								outFields.append(fillNA)					
				else:
					for valueCol in valueCols:
						for pattern in patternSet:
							if IsPatternMatched(pattern,thisPattern):
								printOut=True
								outFields.append(fields[valueCol])
							else:
								outFields.append(fillNA)
				
				if printOut or printRowsWithOnlyNA:
					print >> stdout,fs.join(outFields)	
				
		
			



	fil.close()
	
