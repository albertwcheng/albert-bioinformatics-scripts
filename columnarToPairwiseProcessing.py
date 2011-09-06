#!/usr/bin/env python

from optparse import OptionParser
from sys import *
from math import *
from numpy import *

def printUsageAndExit(parser):
	parser.print_help()
	exit(1)


def curRowData():
	return infileRows[ROWNUM0]
	
def curColData():
	return infileRows[COLNUM0]

def r(x):
	curRow=curRowData()
	try:
		return curRow[x]
	except:
		return curRow[headerColKey[x]]


def rf(x):
	return float(r(x))

def ri(x):
	return int(r(x))

def c(x):
	curCol=curColData()
	try:
		return curCol[x]
	except:
		#try:
		return curCol[headerColKey[x]]
		#except KeyError:
		#	print >> stderr,"data for item at infile row=",ROWNAME,"rownum=",ROWNUM,"column",x,"not found"
		#	exit(1)

def cf(x):
	return float(c(x))
	
def ci(x):
	return int(c(x))
	

if __name__=='__main__':
	parser=OptionParser("usage: %prog [options] infile cmd > outfil")
	parser.add_option("--ifs",dest="IFS",default="\t",help="set input field separator [tab]")
	parser.add_option("--ofs",dest="OFS",default="\t",help="set output field separator [tab]")
	parser.add_option("--header-row",dest="headerRow",default=1,type=int,help="set header row [1]")
	parser.add_option("--start-row",dest="startRow",default=2,type=int,help="set start row [2]")
	parser.add_option("--top-left-corner",dest="topLeftCorner",default=None,help="set the content of top left corner [default use the top left of input file]")
	parser.add_option("--invalid-value",dest="invalidValue",default=None,help="set the invalid value to print [None: quit program]")

	(options,args)=parser.parse_args()
	
	try:
		INFILE,cmd=args
	except:
		printUsageAndExit(parser)
		
	#now load file into mem
	
	
	infileRowNames=[]
	infileRows=[]
	header=[]
	headerColKey=dict()
	
	lino=0
	fil=open(INFILE)
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		
		fields=lin.split(options.IFS)
		if lino==options.headerRow:
			header=fields
			if options.topLeftCorner==None:
				options.topLeftCorner=fields[0]
			for i in range(0,len(header)):
				h=header[i]
				headerColKey[h]=i
		elif lino>=options.startRow:
			infileRowNames.append(fields[0])
			infileRows.append(fields)
		
	
	
	fil.close()
	
	
	print >> stdout,options.OFS.join([options.topLeftCorner]+infileRowNames)
	#now contruct and print matrix
	for ROWNUM0 in range(0,len(infileRows)):
		ROWNUM=ROWNUM0+1
		ROWNAME=infileRowNames[ROWNUM0]
		#print name
		outputv=[ROWNAME]
		for COLNUM0 in range(0,len(infileRows)):
			COLNUM=COLNUM0+1
			COLNAME=infileRowNames[COLNUM0]
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
	
	
	