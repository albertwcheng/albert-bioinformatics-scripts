#!/usr/bin/env python

from sys import *
from getopt import getopt
from albertcommon import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] XYZFile > ZOnXYMatrixOut"
	print >> stderr,"Options:"
	print >> stderr,"--cols. Specify columns [default: 1-3]"
	print >> stderr,"--left-corner label. Specify the label of top left corner [default: matrix]"
	print >> stderr,"--NAValue fillValue. Specify how to fill NA vlaues [default: NA]"
	print >> stderr,"--startRow row. Specify which row to start [default: 1]"
	print >> stderr,"--XInt,--YInt. Treat X or Y values as integers"
	print >> stderr,"--XSorted,--YSorted. Sort X or Y values"
	print >> stderr,"--XFilled,--YFilled. Fill X or Y values"
	print >> stderr,"Filled => Sorted, Int"
	explainColumns(stderr)
	exit()
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],"",["left-corner=","NAValue=","XInt","YInt","XSorted","YSorted","XFilled","YFilled",'startRow=','cols='])
	fs="\t"
	leftCorner="matrix"
	fillNA="NA"
	XInt=False
	YInt=False
	XSorted=False
	YSorted=False
	XFilled=False
	YFilled=False
	startRow=1
	cols="1-3"
	for o,v in opts:
		if o=='--left-corner':
			leftCorner=v
		elif o=='--NAValue':
			fillNA=v
		elif o=='--XInt':
			XInt=True
		elif o=='--YInt':
			YInt=True
		elif o=='--XSorted':
			XSorted=True
		elif o=='--YSorted':
			YSorted=True
		elif o=='--XFilled':
			XFilled=True
		elif o=='--YFilled':
			YFilled=True
		elif o=='--startRow':
			startRow=int(v)
		elif o=='--cols':
			cols=v
	try:
		XYZFile,=args
	except:
		printUsageAndExit(programName)
	
	if XFilled:
		XSorted=True
		XInt=True
	if YFilled:
		YSorted=True
		YInt=True
	
	X=[]
	Y=[]
	Z=dict()
	
	headerRow=1
	
	header,prestarts=getHeader(XYZFile,headerRow,startRow,fs)
	cols=getCol0ListFromCol1ListStringAdv(header,cols)

	lino=0
	fil=open(XYZFile)
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		lin=lin.rstrip("\r\n")
		x,y,z=getSubvector(lin.split(fs),cols)
		if XInt:
			x=int(x)
		if YInt:
			y=int(y)
		if x not in X:
			X.append(x)
		if y not in Y:
			Y.append(y)
		try:
			Zx=Z[x]
		except KeyError:
			Z[x]=dict()
		
		Z[x][y]=z
		
	fil.close()
	
	if XFilled:
		X=range(min(X),max(X)+1)
	elif XSorted:
		X.sort()
		
	if YFilled:
		Y=range(min(Y),max(Y)+1)
	elif YSorted:
		Y.sort()
	
	#now output
	#first row will be leftcorner and x labels
	outputV=[leftCorner]+[str(x) for x in X]
	print >> stdout,fs.join(outputV)
	#>1 row will be Ylabel and Z values
	for y in Y:
		outputV=[str(y)]
		for x in X:
			try:
				outputV.append(Z[x][y])
			except KeyError:
				outputV.append(fillNA)
		print >> stdout,fs.join(outputV)
	
	#end