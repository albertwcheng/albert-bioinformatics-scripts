#!/usr/bin/env python

from optparse import OptionParser
from sys import *
from math import *
from numpy import *

def printUsageAndExit(parser):
	parser.print_help()
	exit(1)


f=float
i=int

def f1(t=str):
	return t(M1[ROWNUM0][COLNUM0])

def f2(t=str):
	return t(M2[ROWNUM0][COLNUM0])
	
def f1f():
	return float(f1())

def f2f():
	return float(f2())

def f1i():
	return int(f1())

def f2i():
	return int(f2())

def loadMatrix(filename,options):
	M=[]
	colnames=[]
	rownames=[]
	topleftcorner=""
	fil=open(filename)
	lino=0
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		fields=lin.split(options.IFS)
		if lino==1:
			topleftcorner=fields[0]
			colnames=fields[1:]
		else:
			rownames.append(fields[0])
			M.append(fields[1:])
	
	
	
	fil.close()
	return topleftcorner,colnames,rownames,M

def dim(M):
	numRows=len(M)
	if numRows>=1:
		numCols=len(M[0])
	else:
		numCols=0
		
	return (numRows,numCols)

if __name__=='__main__':
	parser=OptionParser("usage: %prog [options] infile1 infile2 cmd > outfil\nf1(int) or f1(i) the content of file1 as integer\nf1(f) or f1(float) the content of file1 as float\nfor example: f1()+f2() concatenates the string from file1 and file2 at each cell\nf1(float)/f2(float) divides f1 as a float by f2\n'T' if f1(float)>f2(float) else 'F' writes T if f1 > f2 as floats else it writes F")
	parser.add_option("--ifs",dest="IFS",default="\t",help="set input field separator [tab]")
	parser.add_option("--ofs",dest="OFS",default="\t",help="set output field separator [tab]")
	parser.add_option("--invalid-value",dest="invalidValue",default=None,help="set the invalid value to print [None: quit program]")

	(options,args)=parser.parse_args()
	
	try:
		INFILE1,INFILE2,cmd=args
	except:
		printUsageAndExit(parser)
		
	#now load file into mem
	
	
	topleftcorner1,colnames1,rownames1,M1=loadMatrix(INFILE1,options)
	topleftcorner2,colnames2,rownames2,M2=loadMatrix(INFILE2,options)
	
	numRows1,numCols1=dim(M1)
	
	if dim(M1)!=dim(M2):
		print >> stderr,"file1:",INFILE1,"dim(r,c)=",dim(M1),"!=",INFILE2,"dim=",dim(M2)
		exit(1)
		
	if tuple(colnames1)!=tuple(colnames2):
		print >> stderr,"warning: file1 and file2 column names do not equal file1=",colnames1,"file2=",colnames2
	
	if tuple(rownames1)!=tuple(rownames2):
		print >> stderr,"warning: file1 and file2 row names do not equal file1=",rownames1,"file2=",colnames2
	
	
	print >> stdout,options.OFS.join([topleftcorner1]+colnames1)
	#now contruct and print matrix
	for ROWNUM0 in range(0,numRows1):
		ROWNUM=ROWNUM0+1
		ROWNAME=rownames1[ROWNUM0]
		#print name
		outputv=[ROWNAME]
		for COLNUM0 in range(0,numCols1):
			COLNUM=COLNUM0+1
			COLNAME=colnames1[COLNUM0]
			try:
				valueToPrint=str(eval(cmd))
				outputv.append(valueToPrint)
			except:
				if options.invalidValue==None:
					print >> stderr,"error running",cmd,"at ROWNUM,ROWNAME=",ROWNUM,ROWNAME,"COLNUM,COLNAME=",COLNUM,COLNAME
					exit(1)
				else:
					outputv.append(options.invalidValue)
		print >> stdout,options.OFS.join(outputv)
	
	
	