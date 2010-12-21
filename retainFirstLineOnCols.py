#!/usr/bin/env python

from albertcommon import *
from sys import *
from optparse import OptionParser

if __name__=='__main__':
	programName=argv[0]
	parser=OptionParser(usage="Usage: %prog [options] file colSelector ... > outfile. keep the first line with the specific vector of values specified by the selectors")
	parser.add_option("--fs",dest="fs",default="\t",help="set field separator [tab]")
	parser.add_option("--header-row",dest="headerRow",default=1,type=int,help="set header row [1]")
	parser.add_option("--start-row",dest="startRow",default=2,type=int,help="set start row [2]")	
	options,args=parser.parse_args()
	
	try:
		filename=args[0]
		selectors=args[1:]
	except:
		parser.print_help()
		exit()
		
	selectedCols=[]
	
	header,prestarts=getHeader(filename,options.headerRow,options.startRow,options.fs)
	
	for selector in selectors:
		newCols=getCol0ListFromCol1ListStringAdv(header,selector)
		selectedCols.extend(newCols)

	
	outputHistory=set()
	
	lino=0
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		
		lino+=1
		if lino<options.startRow:
			print >> stdout,lin
			continue
		
		fields=lin.split(options.fs)
		linkey=tuple(getSubvector(fields,selectedCols))
		if linkey in outputHistory:
			continue
		
		print >> stdout,lin
		outputHistory.add(linkey)
		
	fil.close()