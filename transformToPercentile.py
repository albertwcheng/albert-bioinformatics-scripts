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

from getopt import getopt
from sys import *
from albertcommon import *

fs="\t"


programName=argv[0]

startRow=-1
headerRow=1

def getVectorByIndexVector(datavector,indexvector):
	v=[]
	
	for idx in indexvector:
		try:
			v.append(datavector[idx])
		except IndexError:
			print >> stderr,datavector,idx
	return v


def ToStringVectorInPlace(V):
	for i in range(0,len(V)):
		V[i]=str(V[i])

def StringVectorToIntVectorInPlace(V):
	for i in range(0,len(V)):
		V[i]=int(V[i])	

def StringVectorToFloatVectorInPlace(V):
	for i in range(0,len(V)):
		V[i]=float(V[i])	

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] filename valuecols"
	explainColumns(stderr)
	exit()


def transformValueMatrixToRankMatrix(M):
	ncols=len(M[0])
	nrows=len(M)
	
	for c in range(0,ncols):
		if ncols>100:
			if c % 10==1:
				print >> stderr,"transforming column",c
		colvaluesdict=dict()
		valuesRankMap=dict()
		numvalues=0		
		for r in range(0,nrows):
			strv=M[r][c]
			try:
				floatv=float(strv)
				numvalues+=1
				if floatv not in colvaluesdict:
					colvaluesdict[floatv]=1
				else:
					colvaluesdict[floatv]+=1
			except:
				continue


		#now sort
		colvalues=colvaluesdict.keys()
		colvalues.sort()

		#print >> stderr, "colvalues",colvalues
		
		coun=0		
		for colvalue in colvalues:
			covalu=colvaluesdict[colvalue]
			if covalu==1:
				rankscore=(float(coun)+1)/numvalues*100		
			else:
				rankscore=(float(coun)+coun+covalu+1)/numvalues*100/2
			valuesRankMap[colvalue]=rankscore
			coun+=covalu

			#print >> stderr,"setting",colvalue,rankscore

		for r in range(0,nrows):
			strv=M[r][c]
			valueToSet=strv
			try:
				floatv=float(strv)
			except:
				valueToSet='NA'

			if valueToSet!='NA':
				try:
					valueToSet=str(valuesRankMap[floatv])
				except KeyError:
					print >> stderr,"error: float not mapped to rank",floatv
					exit()

						
			M[r][c]=valueToSet





def transformToRank(filename,valuescol,startRow,ostream,fs):
	fil=open(filename)
	lino=0
	
	matrix=[]
	valuesMatrix=[]
	
	for lin in fil:
		lino+=1

		if lino % 1000==1:
			print >> stderr,"reading line",lino
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)

		matrix.append(fields)
		
		if lino<startRow:
			continue

		if len(fields)-1<max(valuescol):
			continue
		values=getVectorByIndexVector(fields,valuescol)
		#StringVectorToFloatVectorInPlace(values,'NA')
		
		valuesMatrix.append(values)
		
	fil.close()

	transformValueMatrixToRankMatrix(valuesMatrix)

	for r,rankrow in zip(range(startRow-1,len(matrix)),valuesMatrix):
		for c,transformedvalue in zip(valuescol,rankrow):
			matrix[r][c]=transformedvalue


	for i in range(0,len(matrix)):
		print >> ostream, fs.join(matrix[i])
	

	
		
		
	
	


if __name__=='__main__':

	


	try:
		opts,args=getopt(argv[1:],'',['startRow=','headerRow'])
		filename,valuecols=args

	except:
		printUsageAndExit(programName)


	for o,v in opts:
		if o=='--startRow':
			startRow=int(v)
		elif o=='--headerRow':
			headerRow=int(v)


	if startRow==-1:
		startRow=headerRow+1


	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	

	valuecols=getCol0ListFromCol1ListStringAdv(header,valuecols)

	transformToRank(filename,valuecols,startRow,stdout,fs)
