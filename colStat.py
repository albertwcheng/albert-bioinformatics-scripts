#!/usr/bin/env python

'''
colStat.py

get the header of a file
 
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


from sys import stderr,stdout,argv,exit
from albertcommon import *
from getopt import getopt

'''
def old_excelColIndex(idx):
	outString=""	
	k,d=divMod(idx,26)
	if k>=1:
		outString=chr(ord('A')+(k-1))
	
	outString+=chr(ord('A')+(d))
	return outString
'''


	

def colStat_Main(filename,rows,cols,separator,OFS):
	try:
		fin=generic_istream(filename)
	except IOError:
		print >> stderr,"Cannot open file",filename
		return
	
	lino=0
	rows.sort()
	maxRow=max(rows)
	for line in fin:
		line=line.rstrip()
		lino+=1
		if lino>maxRow:
			break
	
	
		if lino in rows:
			fields=line.split(separator)			
			print >> stdout, "[:::::"+OFS+"R "+str(lino)+OFS+":::::]"
			print >> stdout, "Index"+OFS+"Excel"+OFS+"Field"
			print >> stdout, "-----"+OFS+"-----"+OFS+"-----"
			if len(cols)==0:
				cols=range(0,len(fields))
			
			for col in cols:
				print >> stdout, str(col+1)+OFS+excelColIndex(col)+OFS+fields[col]
	
	fin.close()

if __name__=="__main__":
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:r:c:o:','')

	rows=[1]
	cols=[]
	separator="\t" #default separator is tab
	osep="\t\t\t"

	if len(args)<1:
		print >> stderr, "Usage:",programName,"filename"
		print >> stderr, "Options:"
		print >> stderr, "-F,-t [separator]"
		print >> stderr," -r [a-b,c...] rows to print [default:1]"
		print >> stderr," -c [a-b,c...] cols to print [default: all]"
		print >> stderr," -o string   output separator string"
	else:
		filename=args[0]
	
		for a,v in optlist:
			if a=="-F" or a=="-t":
				separator=replaceSpecialChar(v)
			elif a=="-r":
				rows=rangeListFromRangeString(v,0)
			elif a=="-c":
				cols=getCol0ListFromCol1ListString(v)
			elif a=="-o":
				osep=replaceSpecialChar(v)


		colStat_Main(filename,rows,cols,separator,osep)
