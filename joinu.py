#!/usr/bin/env python

'''

joinu.py

join substitute allowing unsorted files to be joined.


Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

#imports
from sys import stderr,stdout,argv
from getopt import getopt
from albertcommon import *

#getFileOrderedKeyLines
#open file
#append to keys the keyCol0 col
#append to lines the whole line
#return keys,lines as a tuple
def getFileOrderedKeyLines(filename,keyCol0,separator,keyInternalSeparator,maxKey0,warningLevel,warnDuplicateKeys,stripFields,headerRow,fhreplace):
	try:
		f=open(filename)
	except IOError:
		print >> stderr,"Cannot open file",filename
		exit() #added 2010/8/1
	
	keys=[]
	lines=[]
	
	
	if warningLevel >=1 and warnDuplicateKeys:
		keySet=set()
		dupl=0

	maxFNumber=-1000
	
	
	lino=0 #line counter
	
	for line in f:
		lino+=1
		line=line.rstrip("\r\n") #remove carriage return at end of line
		splits=line.split(separator) #split
		if len(splits)<=maxKey0: #error requesting col out of range, ignore that line
			print >> stderr,filename,"line",lino,"has not enough splits:",splits
			continue
			
		if stripFields:
			stripL(splits)
		
		if lino==headerRow:
			replaceValuesByDict(splits,fhreplace)
				
		maxFNumber=max(maxFNumber,len(splits))	
		key=[]
		for keyCol in keyCol0:
			key.append(splits[keyCol])
		
		key=keyInternalSeparator.join(key)
		
		if warnDuplicateKeys:
			if key in keySet:
				dupl+=1
				if warningLevel>=2:
					print >> stderr,"duplicate key",key,"found in file",filename

			keySet.add(key)

		keys.append(key) #append key extracted from the keyCol0 column to keys
		lines.append(splits) #append line to lines #instead, append fields
	
	
	f.close() #close file

	if warningLevel>=1 and warnDuplicateKeys and dupl>0:
		print >> stderr,dupl,"lines of duplicate keys (not including the orginial ones) found in file",filename

	return keys,lines,maxFNumber #return the tuple
	
	
def stripL(L):
	for i in range(0,len(L)):
		L[i]=L[i].strip()
		
def replaceValuesByDict(L,D):
	if len(D)<1:
		return
	for i in range(0,len(L)):
		if L[i] in D:
			L[i]=D[L[i]]	
					
#getKeyedLines
#open file
#KeyedLines[key][] store lines with the same key in their order of appearance 
#fill up KeyedLines[][]
#return it
def getKeyedLines(filename,keyCol0,separator,keyInternalSeparator,maxKey0,warningLevel,warnDuplicateKeys,stripFields,headerRow,fhreplace):
	try:
		f=open(filename)
	except IOError:
		print >> stderr,"Cannot open file",filename
		exit() #added 2010/8/1
	
	KeyedLines=dict()
	
	if warningLevel>=1 and warnDuplicateKeys:
		dupl=0

	 
	lino=0 #line counter
	maxFNumber=-1000
	for line in f:
		lino+=1
		
		line=line.rstrip("\r\n") #remove carriage return at end of line
		splits=line.split(separator) #split
		if len(splits)<=maxKey0: #requesting out of range, ignore line
			print >> stderr,filename,"line",lino,"has not enough splits:",splits
			continue
		
		
		if stripFields:
			stripL(splits)
		
		if lino==headerRow:
			replaceValuesByDict(splits,fhreplace)
		
		maxFNumber=max(maxFNumber,len(splits))

		key=[]
		for keyCol in keyCol0:
			key.append(splits[keyCol])
		
		key=keyInternalSeparator.join(key)

		
		if not KeyedLines.has_key(key): #if key exist, get the list that store the lines with same key, if not create a new list
			CoKeyRow=[]
			KeyedLines[key]=CoKeyRow
		else:
			if warnDuplicateKeys:
				if warningLevel>=1:
					dupl+=1
					if warningLevel>=2:
						print >> stderr,"duplicate key",key,"found in file",filename
			
			CoKeyRow=KeyedLines[key]
		
		CoKeyRow.append(splits) #append line into the list as fields
		
		
	
	f.close() 
	if warningLevel>=1 and warnDuplicateKeys and dupl>0:
		print >> stderr,dupl,"lines of duplicate keys (not including the orginial ones) found in file",filename

	return KeyedLines,maxFNumber


def removeColumns(fields,col0toRemoveSortedReverse):
	for col0 in col0toRemoveSortedReverse:
		del fields[col0]

def repeat(element,times):
	arr=[]
	for i in range(0,times):
		arr.append(element)

	return arr
	

def joinFiles(filename1,filename2,file1f0,file2f0,separator,printFile2Only,skipKeyColFile2,keyInternalSeparator,warningLevel,includeEveryFile1Rows,File2FillIn,warnDuplicateKeys,replaceFile1ColsByFile2,replaceFile1ColsByFile2Cols,stripFields,f1hreplace,f2hreplace,headerRow):

	
	#get the Keys and lines in order from file1
	File1Keys,File1Lines,maxFNumber1=getFileOrderedKeyLines(filename1,file1f0,separator,keyInternalSeparator,max(file1f0),warningLevel,warnDuplicateKeys,stripFields,headerRow,f1hreplace)
	
	#get the Key => Lines dictionary from file 2
	KeyedLinesFile2,maxFNumber2=getKeyedLines(filename2,file2f0,separator,keyInternalSeparator,max(file2f0),warningLevel,warnDuplicateKeys,stripFields,headerRow,f2hreplace)
	
	#maxColNumber=maxFNumber1+maxFNumber2
	
	file2f0sorted=file2f0[:]
	file2f0sorted.sort()
	file2f0sorted.reverse()
	
	#maxColNumbers=0

	maxJoinedColNumber=-1000
	
	joined_lines=[]

	lino=0

	#for each key and line in the ordered list from file1
	matchedLines=0
	unmatchedLines=0
	for key,line1 in zip(File1Keys,File1Lines):
		lino+=1
		try:
			CoKeyRowsFile2=KeyedLinesFile2[key] #find all the lines with that key in file 2 dictionary
			matchedLines+=1
			if replaceFile1ColsByFile2:
				rowFile2=CoKeyRowsFile2[-1] #the last one used		
				toPrint=line1[:]	
				#print >> stderr,replaceFile1ColsByFile2Cols	

				replaceFile1ColsByFile2_File1Cols,replaceFile1ColsByFile2_File2Cols=replaceFile1ColsByFile2Cols
				for replaceFile1ColsByFile2_File1Col,replaceFile1ColsByFile2_File2Col in zip(replaceFile1ColsByFile2_File1Cols,replaceFile1ColsByFile2_File2Cols):
					
					try:					
						newValue=rowFile2[replaceFile1ColsByFile2_File2Col]				
					except IndexError:
						continue  ##rowFile2 doesn't have that column

					try:
						toPrint[replaceFile1ColsByFile2_File1Col]=newValue
					except IndexError:
						needed=replaceFile1ColsByFile2_File1Col-len(toPrint)
						for x in range(0,needed):
							toPrint.append("")
						toPrint.append(newValue)

				joined_lines.append(toPrint)
			else:
				for rowFile2 in CoKeyRowsFile2:
					toPrint=[] #""
					if not printFile2Only: #print also file 1
						toPrint+=line1
					
					if skipKeyColFile2: #print the key col of file 2 also?
						rowFile2splitsClone=rowFile2[:]
						removeColumns(rowFile2splitsClone,file2f0sorted)
						toPrint+=rowFile2splitsClone
					else:	
						toPrint+=rowFile2
				
					joined_lines.append(toPrint)
					maxJoinedColNumber=max(maxJoinedColNumber,len(toPrint))
				
		except KeyError: #key not found in file2
				unmatchedLines+=1
				
				if warningLevel>=2:
					print >> sys.stderr,"line",lino,"of File 1 with key",key,"not found in File 2"

				if replaceFile1ColsByFile2:
					#simply just output line1 without modification
					joined_lines.append(line1[:])
				else:
					if includeEveryFile1Rows:
						if not printFile2Only:
							toPrint=line1[:]						
							joined_lines.append(toPrint)
							maxJoinedColNumber=max(maxJoinedColNumber,len(toPrint))

							
	if warningLevel>=1:
		print >> sys.stderr,matchedLines,"lines of File1 matched and",unmatchedLines,"lines unmatched"

	#print >> stderr,joined_lines

	for i in range(0,len(joined_lines)):
		toPrint=joined_lines[i]

		if includeEveryFile1Rows:
		#need to fill in
			numColsToFill=maxJoinedColNumber-len(toPrint)
			for j in range(0,numColsToFill):
				toPrint.append(File2FillIn)

		print >> stdout,separator.join(toPrint)


	

def joinu_Main():
	programName=argv[0]
	optlist,argvs=getopt(argv[1:],'1:2:rck:t:h:f:w:W:s',['replace-file1-cols-by-file2-cols-on-joined-items=','r1=','r2=','with=','12='])
	headerRow=1

	if len(argvs)<2:
		print >> stderr,"Usage:",programName," filename1 filename2"
		print >> stderr,"Options:"
		print >> stderr,"-1 col1forFile1 (support multiple columns)"
		print >> stderr,"-2 col1forFile2 (support multiple columns)"
		print >> stderr,"--12 col1for both files"
		print >> stderr,"--r1 A --with B. Replace header field of file1 from A to B"
		print >> stderr,"--r2 A --with B."
		print >> stderr,"-t separator"
		print >> stderr,"-r :print file 2 only"
		print >> stderr,"--replace-file1-cols-by-file2-cols-on-joined-items columns  (keeping all file1 lines, replace only when matched)"
		print >> stderr,"-c :include the key col of file 2"
		print >> stderr,"-k keyInternalSeparator : how to join key column strings"
		print >> stderr,"-h headerRow"
		print >> stderr,"-f placeholder. Fill in the empty columns by placeholder if File1 row is not found in File2"
		print >> stderr,"-w warningLevel. Warning print to stderr. 0=no warning, 1=print the number of lines matched and unmatched at the end, 2=print every instances of unmatching, and the total number at the end"
		print >> stderr,"-Wd warn duplicate keys in files"
		print >> stderr,"-s  strip fields"
		explainColumns(stderr)
		return
		
	filename1,filename2=argvs;
	
	file1f0=[0]
	file2f0=[0]
	separator='\t'
	printFile2Only=False
	skipKeyColFile2=True
	keyInternalSeparator="\t"
	warningLevel=1
	includeEveryFile1Rows=False
	File2FillIn="."
	warnDuplicateKeys=False
	replaceFile1ColsByFile2=False
	replaceFile1ColsByFile2Cols=[]
	stripFields=False
	headerFieldReplaceeSelector=0
	headerFieldReplaceeKey=""
	f1hreplace=dict()
	f2hreplace=dict()
	
	for k,v in optlist:
		if k=="-h":
			headerRow=int(v)
	
		elif k=='-1':
			try:
				file1f0=getCol0ListFromCol1ListString(v)
			except ValueError:
				header,prestarts=getHeader(filename1,headerRow,headerRow+1,separator)
				if stripFields:
					stripL(header)
				replaceValuesByDict(header,f1hreplace)
				file1f0=getCol0ListFromCol1ListStringAdv(header,v)	

		elif k=='-2':	
			try:
				file2f0=getCol0ListFromCol1ListString(v)
			except ValueError:
				header,prestarts=getHeader(filename2,headerRow,headerRow+1,separator)
				if stripFields:
					stripL(header)				
				replaceValuesByDict(header,f2hreplace)
				file2f0=getCol0ListFromCol1ListStringAdv(header,v)				
		elif k=='--12':
			try:
				file1f0=getCol0ListFromCol1ListString(v)
			except ValueError:
				header,prestarts=getHeader(filename1,headerRow,headerRow+1,separator)
				if stripFields:
					stripL(header)
				replaceValuesByDict(header,f1hreplace)
				file1f0=getCol0ListFromCol1ListStringAdv(header,v)
				
			try:
				file2f0=getCol0ListFromCol1ListString(v)
			except ValueError:
				header,prestarts=getHeader(filename2,headerRow,headerRow+1,separator)
				if stripFields:
					stripL(header)				
				replaceValuesByDict(header,f2hreplace)
				file2f0=getCol0ListFromCol1ListStringAdv(header,v)				
		elif k=='-t':
			separator=replaceSpecialChar(v)	
		elif k=='-r':
			printFile2Only=True
			skipKeyColFile2=False
		elif k=='-c':
			skipKeyColFile2=False
		elif k=='-k':
			keyInternalSeparator=replaceSpecialChar(v)
		elif k=='-w':
			warningLevel=int(v)
		elif k=='-f':
			includeEveryFile1Rows=True
			File2FillIn=v
		elif k=='-W':
			if v=='d':			
				warnDuplicateKeys=True
			else:
				print >> stderr,"unknown warning category","-"+k+v
				printUsageAndExit(programName)
		elif k=='--replace-file1-cols-by-file2-cols-on-joined-items':
			replaceFile1ColsByFile2=True
			header,prestarts=getHeader(filename2,headerRow,headerRow+1,separator)
			if stripFields:
				stripL(header)			
			replaceValuesByDict(header,f2hreplace)
			replaceFile1ColsByFile2_File2Cols=getCol0ListFromCol1ListStringAdv(header,v)	
			header,prestarts=getHeader(filename1,headerRow,headerRow+1,separator)
			if stripFields:
				stripL(header)				
			replaceValuesByDict(header,f1hreplace)
			replaceFile1ColsByFile2_File1Cols=getCol0ListFromCol1ListStringAdv(header,v)			
			replaceFile1ColsByFile2Cols=(replaceFile1ColsByFile2_File1Cols,replaceFile1ColsByFile2_File2Cols)
		elif k=='-s':
			stripFields=True
		elif k=='--r1':
			headerFieldReplaceeSelector=1
			headerFieldReplaceeKey=v
		elif k=='--r2':
			headerFieldReplaceeSelector=2
			headerFieldReplaceeKey=v
		elif k=='--with':

			if headerFieldReplaceeSelector==1:
				f1hreplace[headerFieldReplaceeKey]=v
			elif headerFieldReplaceeSelector==2:
				f2hreplace[headerFieldReplaceeKey]=v
			else:
				print >> stderr,"--with not preceded by --r1 or --r2. Abort"
				#printUsageAndExit(programName)
				exit()
								
			headerFieldReplaceeSelector=0
	if warningLevel>0:		
		print >> sys.stderr,"seperator is ["+separator+"]";
	joinFiles(filename1,filename2,file1f0,file2f0,separator,printFile2Only,skipKeyColFile2,keyInternalSeparator,warningLevel,includeEveryFile1Rows,File2FillIn,warnDuplicateKeys,replaceFile1ColsByFile2,replaceFile1ColsByFile2Cols,stripFields,f1hreplace,f2hreplace,headerRow)

if __name__=='__main__':
	joinu_Main()



