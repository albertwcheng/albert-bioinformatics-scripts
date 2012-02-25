#!/usr/bin/env python

from getopt import getopt
from sys import *
from os import system
from os.path import basename
from listCount import removeExtension

def call(s,really,printCmds):

	if printCmds or not really:
		print >> stderr,s
	if really:
		system(s)
	
		

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] file1[=key1] file2[=key2] outprefix"
	print >> stderr,"Options:"
	exit(1)
	
if __name__=='__main__':
	
	headerRow="1"
	file1col="1"
	file2col="1"
	elementStatBase="elementStat.txt"
	listSuffix=".list"
	onlySuffix=".only"
	joinSuffix=".txt"
	pythonCmd=""
	really=True
	printCmds=False
	programName=argv[0]
	opts,args=getopt(argv[1:],'1:2:',['headerRow=','elementStatBase=','listSuffix=','onlySuffix=','joinSuffix=','python=','test','printCmds'])
	
	for o,v in opts:
		if o=='--headerRow':
			headerRow=v
		elif o=='--elementStatBase':
			elementStatBase=v
		elif o=='--listSuffix':
			listSuffix=v
		elif o=='--onlySuffix':
			onlySuffix=v
		elif o=='--joinSuffix':
			joinSuffix=v
		elif o=='-1':
			file1col=v
		elif o=='-2':
			file2col=v
		elif o=='--python':
			pythonCmd=v
		elif o=='--test':
			really=False
		elif o=='--printCmds':
			printCmds=True
	try:
		file1,file2,outprefix=args
	except:
		printUsageAndExit(programName)
	
	if "=" in file1:
		file1,file1label=file1.split("=")
	else:
		file1label=removeExtension(basename(file1))
	
	if "=" in file2:
		file2,file2label=file2.split("=")
	else:
		file2label=removeExtension(basename(file2))
	
	if outprefix[-1]=='/':
		system(pythonCmd+" mkdir.py "+outprefix)
	
	call(pythonCmd+" cuta.py -f"+file1col+" "+file1+" > "+outprefix+file1label+listSuffix,really,printCmds)
	call(pythonCmd+" cuta.py -f"+file2col+" "+file2+" > "+outprefix+file2label+listSuffix,really,printCmds)
	
	call(pythonCmd+" listCount.py --draw-venn --remove-ext --usebasename --headerFrom1To "+headerRow+" --outcombination "+outprefix+","+onlySuffix+" "+file1+"="+file1label+" "+file2+"="+file2label+" > "+outprefix+elementStatBase,really,printCmds)
	
	call(pythonCmd+" joinu.py -1 "+file1col+" -2 "+file2col+" "+file1+" "+file2+" > "+outprefix+file1label+"_"+file2label+joinSuffix,really,printCmds)
	call(pythonCmd+" joinu.py -1 "+file1col+" -2 1 "+file1+" "+outprefix+file1label+onlySuffix+" > "+outprefix+file1label+joinSuffix,really,printCmds)
	call(pythonCmd+" joinu.py -1 "+file2col+" -2 1 "+file2+" "+outprefix+file2label+onlySuffix+" > "+outprefix+file2label+joinSuffix,really,printCmds)
	