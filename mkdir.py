#!/usr/bin/python

from sys import *
from os import *
from os.path import *

if __name__=='__main__':
	programName=basename(argv[0])
	args=argv[1:]
	try:
		pathName,=args
	except:
		print >> stderr,programName,"pathToMake"
		print >> stderr,"recursively make a directory"
		exit()
	
	
	makedirs(pathName)
	
		