#!/usr/bin/env python

from math import *
from sys import *
from getopt import getopt

def log2(x):
	return log(x,2)

def printUsageAndExit(programName):
	print >> stderr,programName,"matrix  [--start-row startRow] [--cols columns (Default:2-_1)|-c conditional|-o conditional-operation|-O non-conditional-operation] ... "
	print >> stderr,"Variables:"
	print >> stderr,"ROW:current row number based 1"
	print >> stderr,"COL:current col number based 1"
	print >> stderr,"HEADERS:header array based 0"
	print >> stderr,"FIELDS:current field array based 0"
	print >> stderr,"ROWNAME:FIELDS[0]"
	print >> stderr,"COLNAME:HEADERS[COL-1]"
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'c:o:O:',['cols=','start-row='])
	
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
	
	headerRow=1	
	startRow=2
	
	operations=[]
	
	currentConditional="True"
	currentColumns="2-_1"
	fs="\t"
	
	
	for o,v in opts:
		if o=='--cols':
			columns=v
		elif o=='--start-row':
			startRow=int(startRow)
		elif o=='-c':
			currentConditional=v
		elif o=='-o':
			operations.append([currentColumns,currentConditional,v])
		elif o=='-O':
			operations.append([currentColumns,"True",v])
	
	HEADERS,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	for i in range(0,len(operations)):
		columns,conditional,operation=operations[i]
		columns=getCol0ListFromCol1ListStringAdv(HEADERS,columns)
		operations[i][0]=columns
	
	
	ROW=0
	fil=open(filename)
	for lin in fil:
		ROW+=1
		if ROW<startRow:
			continue
		lin=lin.rstrip("\r\n")
		FIELDS=lin.split(fs)
		for columns,conditional,operation in operations:
			for column in columns:
				COLUMN=column+1
				ROWNAME=FIELDS[0]
				COLNAME=FIELDS[column]
				if eval(conditional):
					FIELDS[column]=eval(operation)
		
	fil.close()
	