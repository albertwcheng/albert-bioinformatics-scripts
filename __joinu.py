#!/usr/bin/python
############################
# joinu.py
# join unsorted files by field
# (c) Albert W. Cheng
# awcheng@mit.edu
# Version 2
# Updated: 2008-04-01
#############################

#imports
from sys import stderr,stdout,argv
from getopt import getopt
from albertcommon import *

#getFileOrderedKeyLines
#open file
#append to keys the keyCol0 col
#append to lines the whole line
#return keys,lines as a tuple
def getFileOrderedKeyLines(filename,keyCol0,separator,keyInternalSeparator,maxKey0):
	try:
		f=open(filename)
	except IOError:
		print >> stderr,"Cannot open file",filename
	
	keys=[]
	lines=[]
	
	
	lino=0 #line counter
	
	for line in f:
		lino+=1
		line=line.rstrip("\r\n") #remove carriage return at end of line
		splits=line.split(separator) #split
		if len(splits)<=maxKey0: #error requesting col out of range, ignore that line
			print >> stderr,filename,"line",lino,"has not enough splits:",splits
			continue
		
		key=[]
		for keyCol in keyCol0:
			key.append(splits[keyCol])
		
		key=keyInternalSeparator.join(key)
		keys.append(key) #append key extracted from the keyCol0 column to keys
		lines.append(line) #append line to lines
	
	
	f.close() #close file
	return keys,lines #return the tuple
	
#getKeyedLines
#open file
#KeyedLines[key][] store lines with the same key in their order of appearance 
#fill up KeyedLines[][]
#return it
def getKeyedLines(filename,keyCol0,separator,keyInternalSeparator,maxKey0):
	try:
		f=open(filename)
	except IOError:
		print >> stderr,"Cannot open file",filename
	
	KeyedLines=dict()
	
	 
	lino=0 #line counter
	
	for line in f:
		lino+=1 
		line=line.rstrip("\r\n") #remove carriage return at end of line
		splits=line.split(separator) #split
		if len(splits)<=maxKey0: #requesting out of range, ignore line
			print >> stderr,filename,"line",lino,"has not enough splits:",splits
			continue
		
		key=[]
		for keyCol in keyCol0:
			key.append(splits[keyCol])
		
		key=keyInternalSeparator.join(key)

		
		if not KeyedLines.has_key(key): #if key exist, get the list that store the lines with same key, if not create a new list
			CoKeyRow=[]
			KeyedLines[key]=CoKeyRow
		else:
			CoKeyRow=KeyedLines[key]
		
		CoKeyRow.append(line) #append line into the list
		
		
	
	f.close() 
	return KeyedLines


def removeColumns(fields,col0toRemoveSortedReverse):
	for col0 in col0toRemoveSortedReverse:
		del fields[col0]

def joinFiles(filename1,filename2,file1f0,file2f0,separator,printFile2Only,skipKeyColFile2,keyInternalSeparator):

	
	#get the Keys and lines in order from file1
	File1Keys,File1Lines=getFileOrderedKeyLines(filename1,file1f0,separator,keyInternalSeparator,max(file1f0))
	
	#get the Key => Lines dictionary from file 2
	KeyedLinesFile2=getKeyedLines(filename2,file2f0,separator,keyInternalSeparator,max(file2f0))
	
	
	file2f0sorted=file2f0[:]
	file2f0sorted.sort()
	file2f0sorted.reverse()
	
	
	
	#for each key and line in the ordered list from file1
	for key,line1 in zip(File1Keys,File1Lines):
		try:
			CoKeyRowsFile2=KeyedLinesFile2[key] #find all the lines with that key in file 2 dictionary
			for rowFile2 in CoKeyRowsFile2:
				toPrint=""
				if not printFile2Only: #print also file 1
					toPrint+=line1+separator
				if skipKeyColFile2: #print the key col of file 2 also?
					rowFile2splits=rowFile2.split(separator)
					removeColumns(rowFile2splits,file2f0sorted)
					toPrint+=separator.join(rowFile2splits)
				else:
					toPrint+=rowFile2
				print toPrint
		except KeyError: #key not found in file2
			pass


def joinu_Main():
	programName=argv[0]
	optlist,argvs=getopt(argv[1:],'1:2:rc')
	
	if len(argvs)<2:
		print >> stderr,"Usage:",programName," filename1 filename2"
		print >> stderr,"Options:"
		print >> stderr,"-1 col1forFile1 (support multiple columns)"
		print >> stderr,"-2 col1forFile2 (support multiple columns)"
		print >> stderr,"-t separator"
		print >> stderr,"-r :print file 2 only"
		print >> stderr,"-c :include the key col of file 2"
		print >> stderr,"-k keyInternalSeparator : how to join key column strings"
		return
		
	filename1,filename2=argvs;
	
	file1f0=[0]
	file2f0=[0]
	separator='\t'
	printFile2Only=False
	skipKeyColFile2=True
	keyInternalSeparator="\t"
	
	for k,v in optlist:
		if k=='-1':
			file1f0=getCol0ListFromCol1ListString(v)
		elif k=='-2':
			file2f0=getCol0ListFromCol1ListString(v)
		elif k=='-t':
			separator=replaceSpecialChar(v)	
		elif k=='-r':
			printFile2Only=True
			skipKeyColFile2=False
		elif k=='-c':
			skipKeyColFile2=False
		elif k=='-k':
			keyInternalSeparator=replaceSpecialChr(v)
	
	joinFiles(filename1,filename2,file1f0,file2f0,separator,printFile2Only,skipKeyColFile2,keyInternalSeparator)

if __name__=='__main__':
	joinu_Main()



