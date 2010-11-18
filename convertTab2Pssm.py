#!/usr/bin/python

#convertTab2Pssm.py
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


def convertStrMatrixToFloatMatrix(M):
	F=[]
	for mrow in M:
		Frow=[]
		F.append(Frow)
		
		for s in mrow:
			Frow.append(float(s))
	
	
	return F
	
def convertFloatMatrixToStrMatrix(F):
	S=[]
	for frow in F:
		Srow=[]
		S.append(Srow)
		for f in frow:
			Srow.append(str(f))
			
	return S
	
def toPSSM(M):
	ncols=len(M[0])
	nrows=len(M)
	for c in range(0,ncols):
		csum=0.0
		for r in range(0,nrows):
			csum+=M[r][c]
		for r in range(0,nrows):
			M[r][c]/=csum
	
		
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		tabfile,=args
	except:
		print >> stderr,programName,"tabfile > pssmfile"
		exit()
	
	fil=open(tabfile)
	lines=fil.readlines()	
	fil.close()
	
	if len(lines)!=4:
		print >> stderr, "error: tab file format error, line no!=4"
		exit()
	
	
		
	for i in range(0,len(lines)):
		lines[i]=lines[i].strip().split("\t")
		if i==0:
			ncol=len(lines[i])
			if ncol<=1:
				print >> stderr,"error: tab file format error, number of col<=1"
				exit()
		else:
			if ncol!=len(lines[i]):
				print >> stderr,"error: tab file format error, col numbers not consistent thru-out all rows"
				exit()
	
	alphabets=['A','C','G','T']	
	
	hasAlphabet=False
	
	try:	
		testA=float(lines[0][0])
	except ValueError:
		hasAlphabet=True
	
	if hasAlphabet:
		#first col is alphabet check!
		for i in range(0,len(lines)):
			if alphabets[i]!=lines[i][0]:
				print >> stderr,"error: tab file format error, alphabet not in order"
			del lines[i][0]
		
	PSSM=convertStrMatrixToFloatMatrix(lines)
	toPSSM(PSSM)
		
	sPSSM=convertFloatMatrixToStrMatrix(PSSM)

	for sPSSMrow in sPSSM:
		print >> stdout," ".join(sPSSMrow)
	
