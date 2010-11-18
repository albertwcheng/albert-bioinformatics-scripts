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
"""

Take a file with R values and take another file with G values and output a file with ratios (logged) as well as std dev
Albert W. Cheng
Unknown date
Annotated Mar 7 2009

"""
import warnings;
warnings.simplefilter("ignore",DeprecationWarning)

import sys;
from math import log;
from scipy import std;
from scipy import mean;
from math import sqrt;

def stddevN_1(arr):
	N=len(arr);
	return sqrt((std(arr)**2)*N/(N-1));

def ratioPrint(filename1,filename2,startCol1,endCol1,startRow1,base,appendStdDev):
	fin1=open(filename1);
	fin2=open(filename2);

	startCol0=startCol1-1;
	endCol0=endCol1-1;

	logb=log(base);

	row1=0;
	for lin1 in fin1:
		lin1=lin1.strip();
		lin2=fin2.readline();
		lin2=lin2.strip();
		
		row1+=1;
		if(row1<startRow1):
			print >>sys.stdout, lin1,
			if(appendStdDev):
				print >>sys.stdout,"StdDev(A)";
			else:
				print >>sys.stdout,"";	
			continue;

		spliton1=lin1.split("\t");
		spliton2=lin2.split("\t");

		colsnum=len(spliton1);

		if(len(spliton1)<endCol1 or len(spliton2)<endCol1):
			print >>sys.stderr, "spliton size < endCol1: line ignored";
			print >>sys.stdout, lin1;
			continue;
		
		#now print the first cols
		for i in range(0,startCol0):
			print >>sys.stdout, spliton1[i], "\t",
		
		logRList=[];
		#now print the log ratio
		for i in range(startCol0,endCol1):
			logvalue1=log(float(spliton1[i]))/logb;
			logvalue2=log(float(spliton2[i]))/logb;
			logratio=logvalue1-logvalue2;
			logRList.append(logratio);			
			print >> sys.stdout, logratio, "\t",

		#now print the remaining cols;
		for i in range(endCol1,colsnum):
			print >> sys.stdout,spliton1[i], "\t",

		
		if(appendStdDev):
			print >> sys.stdout,stddevN_1(logRList);
		else:
			print >> sys.stdout,"";	
		

	fin1.close();
	fin2.close();

if(len(sys.argv)<8):
	print >> sys.stderr, "Usage: "+sys.argv[0]+" filename1 filename2 startCol1inc endCol1inc startRow1inc base appendstddev=y|n";
else:
	ratioPrint(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),(sys.argv[7]=="y"));
