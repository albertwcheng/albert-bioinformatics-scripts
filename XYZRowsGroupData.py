#!/usr/bin/env python

from sys import *
from getopt import getopt

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['remove-self'])
	removeSelf=False
	for o,v in opts:
		if o=="--remove-self":
			removeSelf=True
	try:
		XYZFile=args[0]
		group1=args[1]
		groups=args[1:]
	except:
		print >> stderr,programName,"XYZFile [--remove-self] mem1,mem2,mem3 ... ..."
		exit(1)
		
	for i in range(0,len(groups)):
		groups[i]=groups[i].split(",")
	
	
	
	withinGroupZ=[]
	notWithinGroupZ=[]
	fil=open(XYZFile)
	for lin in fil:
		X,Y,Z=lin.rstrip("\r\n").split("\t")
		withinGroup=False
		if removeSelf and X==Y:
			continue 
		for group in groups:
			if X in group and Y in group:
				withinGroup=True
			
		if withinGroup:
			withinGroupZ.append(Z)
		else:
			notWithinGroupZ.append(Z)
		
	fil.close()
	
	print >> stdout,"within\tnotWithin"
	for i in range(0,max(len(withinGroupZ),len(notWithinGroupZ))):
		if i>=len(withinGroupZ):
			wz=""
		else:
			wz=withinGroupZ[i]
		if i>=len(notWithinGroupZ):
			nwz=""
		else:
			nwz=notWithinGroupZ[i]
		
		print >> stdout,"\t".join([wz,nwz])
	
	