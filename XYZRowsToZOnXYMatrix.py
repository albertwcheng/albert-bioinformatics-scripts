#!/usr/bin/env python

from sys import *
from getopt import getopt
def printUsageAndExit(programName):
	print >> stderr,programName,"[options] XYZFile > ZOnXYMatrixOut"
	print >> stderr,"Options:"
	print >> stderr,"--left-corner label. Specify the label of top left corner [default: matrix]"
	print >> stderr,"--NAValue fillValue. Specify how to fill NA vlaues [default: NA]"
	exit()
	
if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],"",["left-corner=","NAValue"])
	fs="\t"
	leftCorner="matrix"
	fillNA="NA"
	
	for o,v in opts:
		if o=='--left-corner':
			leftCorner=v
		elif o=='--NAValue':
			fillNA=v
	
	try:
		XYZFile,=args
	except:
		printUsageAndExit(programName)
	
	
	
	X=[]
	Y=[]
	Z=dict()
	
	fil=open(XYZFile)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		x,y,z=lin.split(fs)
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
	
	#now output
	#first row will be leftcorner and x labels
	outputV=[leftCorner]+X
	print >> stdout,fs.join(outputV)
	#>1 row will be Ylabel and Z values
	for y in Y:
		outputV=[y]
		for x in X:
			try:
				outputV.append(Z[x][y])
			except KeyError:
				outputV.append(fillNA)
		print >> stdout,fs.join(outputV)
	
	#end