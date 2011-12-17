#!/usr/bin/env python

'''
cuta.py

advanced cut substitute
updated 7/15/2010
 
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

from getopt import getopt,GetoptError
from albertcommon import *
from sys import stderr, stdout
import sys

def cuta_Main(filename,cols0,fs,ofs,fill_empty,relabelmap,headerRow,ignoreTrunc):
	fil=generic_istream(filename)
	
	relabelmapkeys=relabelmap.keys()
	lrelabelmapkeys=len(relabelmapkeys)
	lino=0
	for line in fil:
		ignoreThisRow=False
		lino+=1		
		line=line.strip("\r\n")
		if fs=="":
			fields=line.split()
		else:
			fields=line.split(fs)
		fieldsOut=[]		
		for col0 in cols0:
			try:
				if lino==headerRow and lrelabelmapkeys>0 and col0 in relabelmapkeys:
					fieldsOut.append(relabelmap[col0])
				else:
					fieldsOut.append(fields[col0])
			except IndexError:
				if fill_empty[0]:
					fieldsOut.append(fill_empty[1])
				else:
					if ignoreTrunc:
						ignoreThisRow=True
						break
					else:
						print >> sys.stderr,"Error: Not enough column. Aborted"
						sys.exit()
						
		if not ignoreThisRow:
			print >> stdout,ofs.join(fieldsOut)
	
	fil.close()

def printUsage(programName):
	print >> stderr,"Usage:",programName,"[options] filename"
	print >> stderr,"Synopsis: Substitute of unix cut command. Extract selected columns and print to standard output."
	print >> stderr,"options:"
	print >> stderr,"-f,--fields  idCols"
	print >> stderr,"--fields-relabel cols/relabel1/relabel2/..."
	print >> stderr,"-d,--sep   separator. set input and output separator. use --use-blank-to-nonblank-transition to set it to any blank characters"
	print >> stderr,"--ofs  ofs. set output separator"
	print >> stderr,"--fs   fs.  set input separator"
	print >> stderr,"--headerRow row. set the header Row"
	print >> stderr,"--sorted.  indicate that the columns are outputed in the order of their indices"
	print >> stderr,"--uniq. indicate that columns are outputed only once"
	print >> stderr,"--sortedUniq. a combination of uniq and sorted flag"
	print >> stderr,"-F,--fill-empty-with sth. fill empty colum with sth"
	print >> stderr,"--ignore-truncated-rows. ignore rows with not enough columns"
	explainColumns(stderr)

if __name__=="__main__":
	optlist,args=getopt(sys.argv[1:],'f:d:F:',["use-blank-to-nonblank-transition","fields=","sep=","ofs=","fs=","headerRow=","sortedUniq","sorted","uniq","fill-empty-with","fields-relabel=","ignore-truncated-rows"])
	if len(args)!=1:
		printUsage(sys.argv[0])
		sys.exit()		
	
	fill_empty=[False,""]
	fieldsTmp=[]
	relabeler=[]
	
	fs="\t"
	ofs="\t"
	headerRow=1
	sortB=False
	uniqB=False
	ignoreTrunc=False
		
	for opt,val in optlist:
		if opt in ["-f","--fields"]:
			fieldsTmp.append(val)
			relabeler.append("")
		elif opt in ["--fields-relabel"]:
			valsplit=val.split("/")
			fieldT=valsplit[0]
			relabel=valsplit[1:]	
			fieldsTmp.append(fieldT)
			relabeler.append(relabel)
		elif opt in ["-d","--sep"]:
			fs=replaceSpecialChar(val)
			ofs=fs
		elif opt=="--ofs":
			ofs=replaceSpecialChar(val)
		elif opt=="--fs":
			fs=replaceSpecialChar(val)
		elif opt=="--headerRow":
			headerRow=int(val)
		elif opt=="--use-blank-to-nonblank-transition":
			fs=""
		elif opt=="--sorted":
			sortB=True
		elif opt=="--uniq":
			uniqB=True
		elif opt=="--sortedUniq":
			sortB=True
			uniqB=True
		elif opt=="-F" or opt=="--fill-empty-with":
			fill_empty=[True,val]
		elif opt=="--ignore-truncated-rows":
			ignoreTrunc=True
				
				
	
	filename=args[0]
	header,prestart=getHeader(filename,headerRow,headerRow,fs)

	if len(fieldsTmp)==0:
		print >> stderr,"no fields given, quit!"
		sys.exit()

	cols0=[]

	relabelmap=dict()
	
	for fieldT,relabel in zip(fieldsTmp,relabeler):
		colsToAdd=getCol0ListFromCol1ListStringAdv(header,fieldT)
		for j in range(0,min(len(relabel),len(colsToAdd))):
			relabelmap[colsToAdd[j]]=relabel[j]
		cols0.extend(colsToAdd)

	if(sortB):
		cols0.sort()
	
	if(uniqB):
		cols0=uniq(cols0)
		

	cuta_Main(filename,cols0,fs,ofs,fill_empty,relabelmap,headerRow,ignoreTrunc)

