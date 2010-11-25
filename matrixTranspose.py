#!/usr/bin/env python

'''

transposeMatrix.py

rotate, flip, invert a matrix from a file and print to STDOUT

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
from getopt import getopt

#read in the content of a file into a 2D array, return the array,nrows,maxncols,minncols (check minncols==maxncols for fillin requirement if neccessary)
def readFileIntoMatrix(filename,sep):
	M=[]
	
	Ncols=0 #store the maximum number of cols
	minNcols=-1

	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split(sep)
		thisNCols=len(fields)
		Ncols=max(Ncols,thisNCols)
		if minNcols==-1:
			minNcols=thisNCols
		else:
			minNcols=min(minNcols,thisNCols)		
		M.append(fields)
			

	fil.close()

	return [M,len(M),Ncols,minNcols]

#read in file into 2D array and fill in such that same cols at all rows, return array, nrows,ncols
def readFileIntoMatrixFillIn(filename,sep,fill):
	M,Nrows,maxNcols,minNcols=readFileIntoMatrix(filename,sep)
	if minNcols!=maxNcols: #fill in needed
		for Mrow in M:
			thisNcols=len(Mrow)
			#fill in			
			for filli in range(thisNcols,maxNcols):
				Mrow.append(fill)

	return [M,len(M),maxNcols]


def matrix_r90(M,nrows,ncols):
	Mp=[]
	MpNRows=ncols
	MpNCols=nrows

	for i in range(0,MpNRows):	
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,MpNCols):
			MpRow.append(M[nrows-j-1][i])

		
	return [Mp,MpNRows,MpNCols]
	
def matrix_transpose(M,nrows,ncols):
	Mp=[]
	MpNRows=ncols
	MpNCols=nrows

	for i in range(0,MpNRows):	
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,MpNCols):
			MpRow.append(M[j][i])

		
	return [Mp,MpNRows,MpNCols]	

def matrix_r90cc(M,nrows,ncols):	
	Mp=[]
	MpNRows=ncols
	MpNCols=nrows

	for i in range(0,MpNRows):	
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,MpNCols):
			MpRow.append(M[j][ncols-i-1])

		
	return [Mp,MpNRows,MpNCols]

def matrix_r180(M,nrows,ncols):
	Mp=[]
	
	for i in range(0,nrows):
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,ncols):
			MpRow.append(M[nrows-i-1][ncols-j-1])

	return [Mp,nrows,ncols]

def matrix_flipH(M,nrows,ncols):
	Mp=[]
	for i in range(0,nrows):
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,ncols):
			MpRow.append(M[i][ncols-j-1])
	return [Mp,nrows,ncols]

def matrix_flipV(M,nrows,ncols):
	Mp=[]
	for i in range(0,nrows):
		MpRow=[]
		Mp.append(MpRow)
		for j in range(0,ncols):
			MpRow.append(M[nrows-i-1][j])

	return [Mp,nrows,ncols]

def printMatrix(stream,M,sep):
	for mrow in M:
		print >> stream,sep.join(mrow)

	
def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"[Options] filename > ofilename"
	print >> stderr,"Description: rotate, flip, invert a matrix from a file and print to STDOUT"
	print >> stderr,"Options:"
	print >> stderr,"--operation <method> or simply --<method>. Define the operation on the matrix. Allows chaining of operations to be done in sequential order"
	print >> stderr,"--no-operation. Overrides all operations and do nothing. Just print using ofs"	
	print >> stderr,"\tMethods:"
	print >> stderr,"\t\tT [default]     Transpose the matrix"
	print >> stderr,"\t\tr90cc           Rotate the matrix 90 counter-clockwise"
	print >> stderr,"\t\tr90             Rotate the matrix 90 clockwise"
	print >> stderr,"\t\tr180            Rotate the matrix 180. i.e., invert"
	print >> stderr,"\t\tflipH           Flip the matrix horizontal"
	print >> stderr,"\t\tflipV           Flip the matrix vertical"
	print >> stderr,"--fs <x>. Specify the input field separator"
	print >> stderr,"--ofs <x>. Specify the output field separator"
	print >> stderr,"--fsofs <x>. Specify both the input and output field separators at the same time"
	print >> stderr,"--fill-with <x>. (default is empty). Make sure the numer of columns are the same before operation"
	exit()




if __name__=='__main__':
	programName=argv[0]
	operationsList=["r90","r90cc","r180","flipH","flipV","T"]
	
	opt,args=getopt(argv[1:],'',['fill-with=','fs=','ofs=','fsofs=','operation=','no-operation']+operationsList)
	
	fillWith=""
	fs="\t"
	ofs="\t"
	
	operations=[]
	defaultOp="T"
	noOp=False

	try:
		for o,v in opt:
			if o=='--fill-with':
				fillWith=replaceSpecialChar(v)
			elif o=='--fs':
				fs=replaceSpecialChar(v)
			elif o=='--ofs':
				ofs=replaceSpecialChar(v)
			elif o=='--fsofs':
				fs=replaceSpecialChar(v)
				ofs=fs
			elif o=='--operation':
				if v not in operationsList:
					print >> stderr,"Operation",v,"unknown"
					printUsageAndExit(programName)

				operations.append(v)
			elif o=="--no-operation":
				noOp=True
			elif len(o)>2 and o[0:2]=='--' and o[2:] in operationsList:
				operations.append(o[2:])
				
	except:
		printUsageAndExit(programName)
	
	try:
		filename,=args
	except:
		printUsageAndExit(programName)

	if len(operations)==0:
		operations=[defaultOp]

	


	#read in the matrix from content of file.
	M,nrows,ncols=readFileIntoMatrixFillIn(filename,fs,fillWith)
	
	
	if not noOp:
		for operation in operations:
			if operation=="r90":
				M,nrows,ncols=matrix_r90(M,nrows,ncols)
			elif operation=="r90cc":
				M,nrows,ncols=matrix_r90cc(M,nrows,ncols)
			elif operation=="r180":
				M,nrows,ncols=matrix_r180(M,nrows,ncols)
			elif operation=="flipH":
				M,nrows,ncols=matrix_flipH(M,nrows,ncols)
			elif operation=="flipV":
				M,nrows,ncols=matrix_flipV(M,nrows,ncols)
			elif operation=="T":
				M,nrows,ncols=matrix_transpose(M,nrows,ncols)

	printMatrix(stdout,M,ofs)
	

