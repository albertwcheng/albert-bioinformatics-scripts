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
from sys import *

def printUsageAndExit(programName):
	print >> stderr,programName,"filename[-:STDIN]"
	print >> stderr,"uniq lines retaining order (input file sorting not required)"
	exit()


programName=argv[0]
args=argv[1:]

def uniqLines(lines):
	lineset=[]
	for line in lines:
		if line not in lineset:
			lineset.append(line)
	
	return lineset

if __name__=='__main__':

	try:
		filename,=args
	except:
		printUsageAndExit(programName)

	fil=generic_istream(filename)
	lines=uniqLines(fil.readlines())
	fil.close()
	
	#for line in lines:
	#	print >> stdout,line,
	stdout.writelines(lines)


