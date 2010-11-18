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

import popen2
from sys import *

def AudicClaverieStatInPlace(XYN1N2):
	r,w,e=popen2.popen3('AudicClaverieStat -interactive')
	linput=len(XYN1N2)
	drow=0
	for x,y,n1,n2 in XYN1N2:
		drow+=1
		#if drow%1000==1:
		#print >> stderr,"feeding in data",drow,"of",linput,x,y,n1,n2 ,"...",
		w.write(str(x)+","+str(y)+","+str(n1)+","+str(n2)+"\n")
		#if drow%1000==1:
		#print >> stderr,"donefeed" 
	w.close()

	lines=r.readlines()
	e.close()
	r.close()
	
	loutput=len(lines)
	
	if loutput!=linput:
		print >> stderr,"error:inconsistent input line number with output line number"
		return 

	for i in range(0,loutput):
		
		xyn1n2=XYN1N2[i]
		lin=lines[i]

		fields=lin.split("\t")
		x,y,n1,n2=xyn1n2
		if int(fields[0])!=x:
			print >> stderr,"error inconsistent input value with check value"
			return
		if int(fields[1])!=y:
			print >> stderr,"error inconsistent input value with check value"
			return			
		if int(fields[2])!=n1:
			print >> stderr,"error inconsistent input value with check value"
			return
		if int(fields[3])!=n2:
			print >> stderr,"error inconsistent input value with check value"
			return
		
		xyn1n2.extend([float(fields[4]),float(fields[5])])
	
	

if __name__=='__main__':
	print >> stderr,"testing AudicClaverieStatInterface from python"
	XYN1N2=[]
	XYN1N2.append([1,14,30,27])
	XYN1N2.append([1,4,30,27])
	XYN1N2.append([100,100,30,27])
	XYN1N2.append([100,110,30,27])
	XYN1N2.append([100,120,30,27])
	XYN1N2.append([100,130,30,27])
	XYN1N2.append([100,140,30,27])
	XYN1N2.append([100,12440,30,27])
	XYN1N2.append([0,0,28,25])
	XYN1N2.append([14,34,25,28])
	for i in range(0,7000):
		XYN1N2.append([368, 843,25, 28 ])
	AudicClaverieStatInPlace(XYN1N2)
	print >> stderr, XYN1N2
