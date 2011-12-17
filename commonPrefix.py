#!/usr/bin/env python

from sys import *
from os.path import *


if __name__=='__main__':
	if len(argv)<2:
		print >> stderr,argv[0],"filename1 filename2 ... filenameN"
		print >> stderr,"output common prefix using os.path.commonprefix"
		exit(1)

	print >> stdout,commonprefix(argv[1:])