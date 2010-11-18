#!/usr/bin/python

'''

get overlapping pieces of intervals from two bed files.

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
from getopt import getopt
from getOverlappingPiecesOfIntervals import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[Options] bedfile"
	print >> stderr,"Options:"
	print >> stderr,"--bin-interval interval [100000] set the interval for binning. Binning is used to accelerate overlaps"
	print >> stderr,"--warn-duplicates turn on warnings for duplicate entries"
	print >> stderr,"--remove-duplicates remove duplicate entries"
	exit()

if __name__=='__main__':

	programName=argv[0]
	opts,args=getopt(argv[1:],'',['warn-duplicates','remove-duplicates','bin-interval='])
	try:
		bedfile,=args
	except:
		printUsageAndExit(programName)

	binInterval=100000
	warnduplicate=False
	appenduplicate=True

	overlapLength=1
	
	addChromIfNeeded=False
	collapsePerBed1=False

	for o,v in opts:
		if o=='--warn-duplicates':
			warnduplicate=True
		elif o=='--remove-duplicates':
			appenduplicate=False
		elif o=='--bin-interval':
			binInterval=int(v)


	print >> stderr,"reading in",bedfile
	bed=readBed(bedfile,appenduplicate,warnduplicate)

	print >> stderr,"making bins"
	bin=binIntv(bed,binInterval)
	print >> stderr,"merge...",
	obed=mergeIntervals(bin,bed)
	#print >> stderr,obed
	#obed=overlapPiecesOfIntervals(bed1,bed2)
	print >> stderr,"... done."
	print >> stderr,"printing"
	printBed(stdout,obed)
