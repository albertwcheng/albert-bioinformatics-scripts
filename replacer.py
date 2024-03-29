#!/usr/bin/env python2.7

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

import sys
from sys import *
#from albertcommon import *
from getopt import getopt

programName=argv[0]
opts,args=getopt(argv[1:],'',['strip-field'])

stripField=False

for o,v in opts:
	if o=='--strip-field':
		stripField=True

try:
	Replacee,Replacer=args
except:
	print >> sys.stderr,"Usage",programName,"[--strip-field] replacee replacer"
	sys.exit()

replacer_dict=dict()

fil=open(Replacer)
for lin in fil:
	lin=lin.rstrip("\r\n")
	fields=lin.split("\t")
	replacer_dict[fields[0]]=fields[1]

fil.close()

lino=0

fil=open(Replacee)
for lin in fil:
	lino+=1	
	lin=lin.rstrip("\r\n")
	fields=lin.split("\t")
	for i in range(0,len(fields)):
		if stripField:
			fields[i]=fields[i].strip()
		if fields[i] in replacer_dict:
			replaca=replacer_dict[fields[i]]
			print >> stderr,"at line",lino,"field",i,fields[i],"replaced by",replaca
			fields[i]=replaca		
			

	print >> sys.stdout,"\t".join(fields)

fil.close()
