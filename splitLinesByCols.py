#!/usr/bin/env python

from albertcommon import *
from sys import *
from getopt import getopt

def printUsageAndExit(programName):
	print >> stderr,programName,"filename outprefix outsuffix cols"
	explainColumns(stderr)
	exit(1)

def getOutFileName(outprefix,outsuffix,keys,fnjoiner):
	return outprefix+fnjoiner.join(keys)+outsuffix
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['fnjoiner=','startRow=','headerRow='])
	fnJoiner="_"
	
	startRow=2
	headerRow=1
	fs="\t"
		
	for o,v in opts:
		if o=='--fnjoiner':
			fnJoiner=v
		elif o=='--startRow':
			startRow=int(v)
		elif o=='--headerRow':
			headerRow=int(v)
	try:
		filename,outprefix,outsuffix,cols=args
	except:
		printUsageAndExit(programName)
		

	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	cols=getCol0ListFromCol1ListStringAdv(header,cols)
	
	seen=set()
	fhandles=dict()
	
	
	fil=open(filename)
	
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		
		if lino%10000==1:
			print >> stderr,"processing line %d" %(lino)
		
		if lino<startRow:
			continue
		
		fields=lin.split(fs)
		keys=tuple(getSubvector(fields,cols))
		outname=getOutFileName(outprefix,outsuffix,keys,fnJoiner)
		if keys not in seen:
			#new file
			seen.add(keys)
			ofil=open(outname,"w")
			for prestart in prestarts:
				print >> ofil,fs.join(prestart)
			fhandles[outname]=ofil
		else:
			#ofil=open(outname,"a")
			ofil=fhandles[outname]
		
		print >> ofil,lin
			
		#ofil.close()
		
			
		
	fil.close()
	
	for outname,ofil in fhandles.items():
		ofil.close()
	