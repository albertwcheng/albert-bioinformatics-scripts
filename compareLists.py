#!/usr/bin/python

'''



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


from sys import *
from getopt import getopt

def indexAll(L,v):
	indices=[]
	start=0
	Llen=len(L)
	try:
		while start<Llen-1:
			ind=L.index(v,start)
			start=ind+1
	except ValueError:
		pass

	return indices

def getOverlapLists(list1,list2):
	list1copy=list1[:]	
	list2copy=list2[:]
	intersect=[]
	list1spec=[]
	list2spec=[]
	#print list1
	#print list2
	for x in list1copy:		
		#indices=indexAll(list2copy,x)
		try:
			i2=list2copy.index(x)		
			intersect.append(x)
			#print >> stderr,"inserting intersect",x
			#print >> stderr,"a remove",list2copy,i2
			del list2copy[i2]
			#print >> stderr,"b"
		except ValueError:
			list1spec.append(x)

	list2spec=list2copy
	#union=intersect+list1spec+list2spec

	return [intersect,list1spec,list2spec] #,union]

def writeFile(filename,lines):
	fil=open(filename,'w')
	fil.writelines(lines)
	fil.close()


def printUsageAndExit(programName):
	print >> stderr,programName,"[options] file1 file2 ..."
	print >> stderr, "Options:"
	print >> stderr,"--headerFrom1To n  use row 1 to row n of file 1 as header , do not compare these lines in all files, just directly output to each output files"	
	print >> stderr,"--outprefix fileprefix use fileprefix instead of lfilename_rfilename for the output files"
	print >> stderr,"--outsuffix filesuffix use filesuffix instead of .txt"
	exit()

if __name__=='__main__':
	programName=argv[0]
	headerFrom1To=-1
	defaultoutprefix="____________"
	outprefix=defaultoutprefix
	outsuffix=".txt"
	
	try:
		opts,args=getopt(argv[1:],'',['headerFrom1To=','outprefix=','outsuffix='])
		for o,v in opts:
			if o=='--headerFrom1To':
				headerFrom1To=int(v)
			elif o=='--outprefix':
				outprefix=v
			elif o=='--outsuffix':
				outsuffix=v

		filenames=args
	except:
		printUsageAndExit(programName)

	
	if len(filenames)<2:
		print >> stderr,"requires more than more file to compare. has only got",filenames

	filerecords=dict()
	firstFile=True
	header=[]

	for filename in filenames:
		fil=open(filename)
		origlines=fil.readlines()
		fil.close()

		if headerFrom1To>=0:
			if firstFile:
				header=origlines[0:headerFrom1To]
			
			del origlines[0:headerFrom1To]
		
		filerecords[filename]=list(set(origlines))
		firstFile=False

	for i in range(0,len(filenames)-1):
		for j in range(i+1,len(filenames)):
			lfilename=filenames[i]
			rfilename=filenames[j]
			print >> stderr,"comparing",lfilename,rfilename
			intersect,list1spec,list2spec=getOverlapLists(filerecords[lfilename],filerecords[rfilename])
			if outprefix==defaultoutprefix:
				lfilename=lfilename.split("/")
				lfilename=lfilename[len(lfilename)-1]
				rfilename=rfilename.split("/")
				rfilename=rfilename[len(rfilename)-1]
				outprefixuse=lfilename+"_"+rfilename
			else:
				outprefixuse=outprefix

			writeFile(outprefixuse+"_intersect"+outsuffix,header+intersect)
			writeFile(outprefixuse+"_list1spec"+outsuffix,header+list1spec)
			writeFile(outprefixuse+"_list2spec"+outsuffix,header+list2spec)
	
			#writeFile(outprefixuse+"_union.txt",union)		
			
	
