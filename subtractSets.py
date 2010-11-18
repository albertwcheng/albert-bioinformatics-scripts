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


def readToSet(S,filename):
	fil=open(filename)
	for lin in fil:
		lin=lin.strip()
		S.add(lin)
	fil.close()
	



if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		subtractee=args[0]
		subtractors=args[1:]
		firstSubtractor=subtractors[0]
	except:
		print >> stderr,programName,"subtractee subtractors... > out"
		exit()

	subtracteeSet=set()
	
	print >> stderr,"read in subtractee set",subtractee
	readToSet(subtracteeSet,subtractee)
	
	subtractorSet=set()

	for subtractor in subtractors:
		print >> stderr,"read in subtractor set",subtractor
		readToSet(subtractorSet,subtractor)

	print >> stderr,"do subtraction and output"
	
	subtracteeSet-=subtractorSet

	for lin in list(subtracteeSet):
		print >> stdout,lin



			
		
	
