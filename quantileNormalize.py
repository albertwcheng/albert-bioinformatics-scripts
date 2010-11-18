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

#
#
#
#  quantileNormalizeMInPlace(M,method="min,max,mean,sum,rank")
#  M row=samples col=genes
#           gene1  gene2 gene3 ....
#  sample1  value   ....
#  sample2    :  ':.
#  sample3    :     ':.
#   :
#   :


def compare2ndElement(x,y):
	xv=x[1]
	yv=y[1]
	if xv>yv:
		return 1
	elif xv==yv:
		return 0
	else: #xv<yv
		return -1

def Mi2MInPlace(Mi,M):
	for (MiRow,MRow) in zip(Mi,M):
		for i,val in MiRow:
			MRow[i]=val
	
def M2Mi(M):
	Mi=[]
	for row in M:
		newMiRow=[]
		Mi.append(newMiRow)
		for i in range(0,len(row)):
			newMiRow.append([i,row[i]])
	
	return Mi


def fillNormalizer(Mi,normalizer,method):

	numsamples=len(Mi)
	numvalues=len(Mi[0])
	
	methods={"min":-1,"mean":0,"max":1,"sum":2,"rank":3}
	
	try:
		method=methods[method.lower()]
	except KeyError:
		print >> stderr,"undefined method for normalizer:",method
		exit()
	
	for i in range(0,numvalues):
		SUM=0.0
		MINV=""
		MAXV=""
		
		for j in range(0,numsamples):
			Miji=Mi[j][i][1]
			
			SUM+=Miji
			if MINV=="":
				MINV=Miji
			else:
				MINV=min(MINV,Miji)
				
			if MAXV=="":
				MAXV=Miji
			else:
				MAXV=max(MAXV,Miji)
	
		if method==-1:
			normalizer.append(MINV)
		elif method==0:
			normalizer.append(SUM/numsamples)
		elif method==1:
			normalizer.append(MAXV)
		elif method==2:
			normalizer.append(SUM)
		elif method==3:
			normalizer.append(i+1)

def printM(stream,M):
	if len(M)<1:
		return
		
	numsamples=len(M)
	numvalues=len(M[0])
	
	for i in range(0,numvalues):
		print >> stream,str(M[0][i]),
		for j in range(1,numsamples):
			print >> stream,"\t"+str(M[j][i]),
			
		print >> stream,""
		
	print >> stream,""


	
def quantileNormalizeMInPlace(M,method):
#	print >>stderr,"M before normalization"
#	printM(stderr,M)

	Mi=M2Mi(M)
	
#	print >> stderr,"Mi beforeSort"
#	printM(stderr,Mi)
	
	quantileNormalizeMiInPlace(Mi,method)
	
#	print >> stderr,"Mi afterQuantile"
#	printM(stderr,Mi)	
	
	Mi2MInPlace(Mi,M)
	
#	print >>stderr,"M after normalization"
#	printM(stderr,M)	
	
def quantileNormalizeMiInPlace(Mi,method):
	if len(Mi)<2:
		return
		
	numvalues=len(Mi[0])
	
	normalizer=[]
		
	#now sort by quantile
	for MiRow in Mi:
		MiRow.sort(compare2ndElement)
	
#	print >> stderr,"Mi afterSort"
#	printM(stderr,Mi)
	
	#now normalize
	fillNormalizer(Mi,normalizer,method)
	
#	print >> stderr,"normalizer"
#	printM(stderr,[normalizer])
	
	#now redistribute values
	for MiRow in Mi:
		for i in range(0,numvalues):
			MiRow[i][1]=normalizer[i]
