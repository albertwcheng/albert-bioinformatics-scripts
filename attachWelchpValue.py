#!/usr/bin/env python

'''

 attach welch t-test (two groups) p-value to new col
 Albert W. Cheng
 Annotated Mar 7 2009



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


import warnings;
warnings.simplefilter("ignore",DeprecationWarning)

import welchttest;
import sys;
from getopt import getopt;

def attachWelchpValue(filename,cols1,cols2,startRow1,sortByFDR):
	fin=open(filename);
	lino=0;	
	
	pvaluesMap=dict()
	orderedAsInFile=[]
	#[pvalue][ [line,p-value,FDR] ]
	
	for line in fin:
		line=line.strip();
		lino+=1;
		if lino<startRow1:
			print >> sys.stdout, line, "\tWelch p-value\tWelch FDR";
			continue;
		spliton=line.split("\t");
		arr1=[];
		arr2=[];

		for i0 in cols1:
			arr1.append(float(spliton[i0]));
		
		for i0 in cols2:
			arr2.append(float(spliton[i0]));
		
		welchRes=welchttest.welchs_approximate_ttest_arr(arr1,arr2);
		pval=welchRes[3];
	
		try:		
			copvalues=pvaluesMap[pval]
		except KeyError:
			copvalues=[]
			pvaluesMap[pval]=copvalues
		thisEntry=[line,pval,0]
		copvalues.append(thisEntry)
		orderedAsInFile.append(thisEntry)			
		#print >> sys.stdout, line, "\t", str(pval);		
		
		
	fin.close();

	totalEntry=len(orderedAsInFile)
	nAlready=0
	
	
	
	#Now cal FDR and output

	sortedpvalues=pvaluesMap.keys()
	sortedpvalues.sort()

	for pval in sortedpvalues:
		copvalues=pvaluesMap[pval]	
		lcopvalues=len(copvalues)
		nAlready+=lcopvalues		
		FDR=totalEntry*float(pval)/nAlready
		for copvalue in copvalues:
			copvalue[2]=FDR
			
	if sortByFDR:
		for pval in sortedpvalues:
			copvalues=pvaluesMap[pval]
			for copvalue in copvalues:
				line,pval,FDR=copvalue
				print >> sys.stdout, line+"\t"+str(pval)+"\t"+str(FDR)

	else:
		for line,pval,FDR in orderedAsInFile:
			print >> sys.stdout, line+"\t"+str(pval)+"\t"+str(FDR)


programName=sys.argv[0]

if(len(sys.argv)<5):
	print >>sys.stderr, "Usage: "+str(programName)+"-[s] filename [cols1,..] [cols2,...] startRow1";
	print >>sys.stderr, "Options:"
	print >> sys.stderr,"-s sort by p-value"
	exit();

optlist, args=getopt(sys.argv[1:],'s')

sortByFDR=False

for k,v in optlist:
	if k=='-s':
		sortByFDR=True



cols1=[];
cols2=[];
colstr=args[1].split(",");
for s in colstr:
	cols1.append(int(s)-1);

colstr=args[2].split(",");
for s in colstr:
	cols2.append(int(s)-1);

attachWelchpValue(args[0],cols1,cols2,int(args[3]),sortByFDR);

