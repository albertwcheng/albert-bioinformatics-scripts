#!/usr/bin/env python

'''

addIndexToCol.py

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

from optparse import OptionParser
from sys import *
from albertcommon import *

def printUsageAndExit(parser):
	parser.print_help(stderr)
	explainColumns(stderr)
	exit()


if __name__=='__main__':
	usage="usage: %prog [options] filename col"+\
"""

Add in index for values in specified column

"""
	parser=OptionParser(usage,add_help_option=False)
	parser.add_option("-h","--help",dest="help",default=False,action="store_true",help="show this help message and exit")
	parser.add_option("--fs",default="\t",dest="fs",help="set field separator. Default is tab")
	parser.add_option("--start-base",default="1",type="string",dest="startBase",help="set the starting index. Default is 1. Can use excel style. If use excel style, the --excel-style flag is auto set to on")
	parser.add_option("--header-row",default=1,type="int",dest="headerRow",help="set the header row. Default is 1")
	parser.add_option("--start-row",default=2,type="int",dest="startRow",help="set the starting row. Default is 2")
	parser.add_option("--trim-name",default=False,dest="trimName",action="store_true",help="trim name such that spaces in prefix and suffix are removed")
	parser.add_option("--name-index-separator",default=".",dest="nameIndexSeparator",help="set the separator (joiner) between the name and the index")
	parser.add_option("--excel-style",default=False,dest="excelStyle",action="store_true",help="instead of number use excel style, from A to Z,then AA,...")
	parser.add_option("--lowercase",default=False,dest="excelStyleLowercase",action="store_true",help="use lower case for excel style. only valid when --excel-style is set")
	parser.add_option("--prepend",default="",dest="prefix",help="prepend value with a prefix. Default no prepending")
	parser.add_option("--append",default="",dest="suffix",help="append value with a suffix. Default no appending")
	parser.add_option("--only-idx-to-dup",default=False,action="store_true",dest="onlyIdxDup",help="only append a index to duplicates")
	(options,args)=parser.parse_args()

	if options.help:
		printUsageAndExit(parser)

	try:
		filename,col=args
	except:
		printUsageAndExit(parser)

	fs=replaceSpecialChar(options.fs)
	header,prestarts=getHeader(filename,options.headerRow,options.startRow,fs)
	col=getCol0ListFromCol1ListStringAdv(header,col)[0]

	try:
		options.startBase=int(options.startBase)
	except ValueError:
		#using excel base
		options.startBase=excelIndxToCol0(options.startBase)
		#if startbase is excel style, then turn on excelstyle display
		options.excelStyle=True
		#print >> stderr,"s=",options.startBase	

	itemCounter=dict()
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1		
		lin=lin.rstrip("\r\n")
		if lino<options.startRow:
			print >> stdout,lin
			continue		
		fields=lin.split(fs)
		
		# set up a library
		thisName=fields[col]
		
		if options.trimName:
			thisName=thisName.strip()

		try:
			thisItemCount=itemCounter[thisName]
			itemCounter[thisName]+=1
		except:
			thisItemCount=0
			itemCounter[thisName]=1
		
		
		indxToDisplay=thisItemCount+options.startBase
		if options.excelStyle:
			indxToDisplay=excelColIndex(indxToDisplay)
			if options.excelStyleLowercase:
				indxToDisplay=indxToDisplay.lower()
		
		
		
		if options.onlyIdxDup and thisItemCount==0:
			sindxToDisplay=""
		else:
			sindxToDisplay=options.nameIndexSeparator+str(indxToDisplay)
		fields[col]=options.prefix+thisName+sindxToDisplay+options.suffix
		print >> stdout,fs.join(fields)

	fil.close()
	
	
