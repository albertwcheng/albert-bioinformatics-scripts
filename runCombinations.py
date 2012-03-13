#!/usr/bin/env python

from sys import *
from os import *
from albertcommon import *

def printUsageAndExit(programName):
	print >> stderr,programName,"command args..."
	print >> stderr,"combinations encoded by x|y|z"
	exit()
	
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	#argIndex=[]
	argCombinations=[]
	
	if len(args)==0:
		printUsageAndExit(programName)
	
	for arg in args:
		if arg=="|":
			thisArgs=["|"]
		else:
			thisArgs=arg.split("|")
		argCombinations.append(thisArgs)
	
	argCombinations=findAllCombinations(argCombinations)
	for argCombination in argCombinations:
		#for i in range(0,len(argCombination)):
		#	if argCombination[i]!='"':
		#		argCombination[i]='"'+argCombination[i]+'"'
		
		command=" ".join(argCombination)
		#print >> stderr,command
		system(command)