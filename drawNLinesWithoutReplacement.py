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
import random
import time
from getopt import getopt

programName=argv[0]
opts,args=getopt(argv[1:],'',['header='])

header=0

try:
	filename,ndraws=args
except:
	print >> stderr,"Usage",programName,"[--header #lines] filename ndraws"
	print >> stderr,"default no header. ndraws do not include header rows"
	exit()

for o,v in opts:
	if o=='--header':
		header=int(v)


ndraws=int(ndraws)

random.seed(time.time())

fil=open(filename)
lines=fil.readlines()
fil.close()


if header>0:
	#print header lines directly and remove from draws
	for i in range(0,header):
		print >> stdout,lines[i].rstrip("\r\n")
	
	del lines[:header]


if ndraws>len(lines):
	print >> stderr,"ndraws > number of lines. Abort","ndraws:",ndraws,"num lines:",len(lines)
	exit()

def drawALine(lines):
	chosen=random.randint(0,len(lines)-1)
	chosenline=lines[chosen]
	del lines[chosen] #remove the chosen line: draw without replacement
	return chosenline
	
	
for i in range(0,ndraws):
	print >> stdout, drawALine(lines).rstrip("\r\n")

