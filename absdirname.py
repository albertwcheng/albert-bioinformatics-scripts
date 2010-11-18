#!/usr/bin/python

from sys import *
from os.path import *

def getDirName(relPath):
	absPath=abspath(relPath)
	dirName=dirname(absPath)
	return dirName

if __name__=='__main__':
	programName=basename(argv[0])
	args=argv[1:]
	try:
		pathName,=args
	except:
		print >> stderr,programName,"relpathOrAbsPathOfFile"
		exit(1)
	
	if not exists(pathName):
		print >> stderr,"path",pathName,"not reachable"
		exit(1)
		
	dirName=getDirName(pathName)

	print >> stdout,dirName