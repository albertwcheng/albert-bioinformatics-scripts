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

from pylab import randn
from sys import *
from albertcommon import *

def randn_with_mean_sd(miu,sd,rep):
	return randn(rep)*sd+miu
	

def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"infile mean sd > outfile"	
	exit()

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	sep="\t"
	try:
		infile,mean,sd=args
	except:
		printUsageAndExit(programName)
	
	mean=float(mean)
	sd=float(sd)
	
	lino=0
	fil=generic_istream(infile)
	for lin in fil:
		lino+=1
		fields=lin.rstrip("\r\n").split(sep)
		numFields=len(fields)
		
		if lino>1:
			randnums=randn_with_mean_sd(mean,sd,numFields-1)
			for i in range(1,numFields):
				try:
					fields[i]=str(float(fields[i])+randnums[i-1])
				except:
					pass
					
		print >> stdout,sep.join(fields)
			
	fil.close()