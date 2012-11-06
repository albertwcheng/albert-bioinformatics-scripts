#!/usr/bin/env python

from math import *
from sys import *
from getopt import getopt
from albertcommon import *

def log2(x):
	return log(x,2)

def printUsageAndExit(programName):
	print >> stderr,programName,"matrix1 matrix2 ... matrixN  [--rows rows (format start-[end] Default: 2-)|--cols columns (Default:2-_1)|-c conditional|-o conditional-operation|-O non-conditional-operation|-v conditional value|-V non-conditional-value] ... "
	print >> stderr,"Variables:"
	print >> stderr,"ROW:current row number based 1"
	print >> stderr,"COL:current col number based 1"
	print >> stderr,"HEADERS[i]:header array based 0"
	print >> stderr,"FIELDS[i]:current field array based 0"
	print >> stderr,"ROWNAME[i]:FIELDS[i][0]"
	print >> stderr,"COLNAME[i]:HEADERS[i][COL-1]"
	print >> stderr,"X[i]:current field FIELDS[i][COL-1]"
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'c:o:O:v:V:',['cols=','rows='])
	
	try:
		filenames=args
		if len(filenames)==0:
			raise TypeError
	except:
		printUsageAndExit(programName)
	
	
	
	headerRow=1	
	startRow=2
	
	operations=[]
	
	currentConditional="True"
	currentColumns="2-_1"
	currentRows="2-"
	fs="\t"
	
	
	for o,v in opts:
		if o=='--cols':
			currentColumns=v
		#elif o=='--start-row':
			#startRow=int(startRow)
		elif o=='-c':
			currentConditional=v
		elif o=='-o':
			operations.append([currentColumns,currentRows,currentConditional,v])
		elif o=='-O':
			operations.append([currentColumns,currentRows,"True",v])
		elif o=='-v':
			operations.append([currentColumns,currentRows,currentConditional,"'"+v+"'"])
		elif o=='-V':
			operations.append([currentColumns,currentRows,"True","'"+v+"'"])

		elif o=='--rows':
			currentRows=v
	
	HEADERS,prestarts=getHeader(filenames[0],headerRow,startRow,fs)
	
	minRow=None
	maxRow=None
	
	for i in range(0,len(operations)):
		columns,rows,conditional,operation=operations[i]
		rows=rows.split("-")
		if rows[0]=="":
			rowStart=1
		else:
			rowStart=int(rows[0])
		

		
		if len(rows)==1:
			rowEnd=rowStart
		else:
			if rows[1]=="":
				rowEnd=-1
				
			else:
				rowEnd=int(rows[1])
		
		
		if i==0:
			minRow=rowStart
			maxRow=rowEnd
		else:	
			minRow=min(rowStart,minRow)		
			if maxRow!=-1:
				maxRow=max(rowEnd,maxRow)
		
		rows=(rowStart,rowEnd)	
		columns=getCol0ListFromCol1ListStringAdv(HEADERS,columns)
		operations[i][0]=columns
		operations[i][1]=rows
		
		
	
	ROW=0
	
	fils=[]
	
	for filename in filenames:
		fils.append(open(filename))
	
	for lin in fils[0]:
		
		ROW+=1
		lin=lin.rstrip("\r\n")
		
		FIELDS=[lin.split(fs)]
		
		#now read other files
		for i in range(1,len(fils)):
			lin=fils[i].readline()
			lin=lin.rstrip("\r\n")
			FIELDS.append(lin.split(fs))
		

		
		if ROW>=minRow and (maxRow==-1 or ROW<=maxRow):
			for columns,rows,conditional,operation in operations:
				
				if ROW<rows[0] or (rows[1]!=-1 and ROW>rows[1]):
					#out of range
					continue
				
				for column in columns:
					COLUMN=column+1
					
					
					ROWNAME=[f[0] for f in FIELDS]
					COLNAME=HEADERS[column]
					X=[f[column] for f in FIELDS]
					
					
					if eval(conditional):
						try:
							FIELDS[0][column]=eval(operation)
						except:
							for i in range(0,len(X)):
								if "." in X[i]:
									X[i]=float(X[i])
								else:
									X[i]=int(X[i])
									
							FIELDS[0][column]=eval(operation)
								
		print >> stdout,"\t".join(toStrList(FIELDS[0]))
		
	for fil in fils:
		fil.close()
	