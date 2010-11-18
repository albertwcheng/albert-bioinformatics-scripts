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


from sys import *
from math import log
#takes in Biobase matrix and background frequency converts into logodd for MEME suite


alphMap={"A":0,"C":1,"G":2,"T":3}
indxMap={0:"A",1:"C",2:"G",3:"T"}
	
def getRawBiobaseMatrix(filename):
	fil=open(filename)
	lino=0

	headerMap=[]
	mat=[]
	#turn into matrix of 
	#[ [A,C,G,T] per row ] 
	for lin in fil:
		lino+=1
		lin=lin.strip()
		fields=lin.split()
		for i in range(0,4):
			fields[i]=fields[i].strip()
			
		if lino==1:
			for i in range(0,4):
				
					print >> stderr,"dst=",fields[i]
					dst=alphMap[fields[i]]
					headerMap.append(dst)
					
			print >> stderr, "headerMap:",headerMap
		else:
			
			row=[0,0,0,0]
			fields=fields[0:len(headerMap)]
			print >> stderr,fields
			for field,dst in zip(fields,headerMap):
				val=int(field)
				row[dst]=val
				print >> stderr,indxMap[dst]+":"+field
			mat.append(row)
			
	fil.close()
	
	#now normalize to one
	return mat

		

def printUsageAndExit(programName):
	print >> stderr,programName,"biobase > output"
	exit()
	
if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	
	try:
		biobasefile,=args
	except:
		printUsageAndExit(programName)
		
	mat=getRawBiobaseMatrix(biobasefile)
	
	lmatrix=len(mat)
	hmatrix=len(mat[0])
	for i in range(0,hmatrix):
		alpha=indxMap[i]
		output=[alpha]
		for j in range(0,lmatrix):
			output.append(str(mat[j][i]))

		print >> stdout,"\t".join(output)




		
