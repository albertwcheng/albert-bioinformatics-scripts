#!/usr/bin/env python

from sys import *
from os.path import *
from os import *


if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		fileName,=args
	except:
		print >> stderr,"Usage:",programName,"fileName"
		print >> stderr,"Get the absoulate path of file"
		exit()

	print >> stdout,abspath(fileName)
