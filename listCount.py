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
from albertcommon import *


def printUsageAndExit(programName):
	print >> stderr,programName,"[options] file1 file2 ... > outfile (a union of all lines with their counts in each file"
	print >> stderr, "Options:"
	print >> stderr,"--headerFrom1To n  use row 1 to row n of file 1 as header , do not compare these lines in all files, just directly output to each output files"	
	print >> stderr,"--outcombination fileprefix,filesuffix"
	print >> stderr,"--suppress-stat no printing membership table to stdout"
	print >> stderr,"--remove-ext-on-stdout-labels remove the file extension on stdout header labels for filenames"
	print >> stderr,"--name-content label   give the non-headed content a label"
	print >> stderr,"--maxcountTo1  make counts into 1: with line, 0: without line"
	exit()

def fillListInPlace(L,length,element):
	while len(L)<length:
		L.append(element)
		
def getSubvectorGe1(L,selector):
	sV=[]
	for l,s in zip(L,selector):
		if s>=1:
			sV.append(l)
			
	return sV

if __name__=='__main__':
	programName=argv[0]
	headerFrom1To=-1
	outcombination=""
	maxcountTo1=False
	stdoutPrint=True
	removeExtensionOnStdOut=False
	fs="\t"
	contentName="content"
	try:
		opts,args=getopt(argv[1:],'',['headerFrom1To=','outcombination=','suppress-stat','remove-ext-on-stdout-labels','name-content=','maxcountTo1'])
		for o,v in opts:
			if o=='--headerFrom1To':
				headerFrom1To=int(v)
			elif o=='--outcombination':
				outcombination=v.split(",")
			elif o=='--suppress-stat':
				stdoutPrint=False
			elif o=='--remove-ext-on-stdout-labels':
				removeExtensionOnStdOut=True
			elif o=='--name-content':
				contentName=v
			elif o=='--maxcountTo1':
				maxcountTo1=True

		filenames=args
	except:
		printUsageAndExit(programName)

	
	if len(filenames)<2:
		print >> stderr,"requires more than more file to compare. has only got",filenames
		printUsageAndExit(programName)

	
	firstFile=True
	header=[]

	line_count=dict()
	

	numfiles=len(filenames)
	

	for filno in range(0,numfiles):
		filename=filenames[filno]		
		#print >> stderr,"reading file",filno,":",filename

		fil=open(filename)
		origlines=fil.readlines()
		fil.close()

		if headerFrom1To>=0:
			if firstFile:
				header=origlines[0:headerFrom1To]
			
			del origlines[0:headerFrom1To]
		
		for lin in origlines:
			if not line_count.has_key(lin):
				#new line
				line_count[lin]=[]
			
			#fill up [ lin => .... 0 0 0 1 ]
			if len(line_count[lin])==filno+1:
				if not maxcountTo1:
					line_count[lin][-1]+=1
			else:	
				fillListInPlace(line_count[lin],filno,0)
				line_count[lin].append(1)
			

		firstFile=False
	

	ofilehandles=dict()	
	#now finish up by filling up every record to have same number of cols:
	#now output to stdout the union list
	
	if removeExtensionOnStdOut:
		labels=[]
		for filename in filenames:
			labels.append(".".join(filename.split(".")[:-1]))
	else:
		labels=filenames

	if stdoutPrint:
		for headerline in header:
			print >> stdout, headerline.rstrip("\r\n")+fs+(fs.join(labels))
		else:
			print >> stdout,contentName+fs+(fs.join(labels))
	

	for lin,counter in line_count.items():
		fillListInPlace(counter,numfiles,0)
		if outcombination!="":
			ofilename=outcombination[0]+("_".join(getSubvectorGe1(filenames,counter)))+outcombination[1]
			if ofilename not in ofilehandles:
				#print >> stdout,"opening ofile=",ofilename
				ofil=open(ofilename,"w")
				ofilehandles[ofilename]=[ofil,0]
				linc=0

				if len(header)>0:
					ofil.writelines(header)

			else:
				ofil,linc=ofilehandles[ofilename]
			
			ofil.write(lin)
			ofilehandles[ofilename][1]=linc+1
		if stdoutPrint:
			print >> stdout,lin.rstrip("\r\n")+fs+(fs.join(toStrVector(counter)))

	#print >> stderr,line_count	
			
	#now close all openfiles
	for filename,rec in ofilehandles.items():
		ofil,linc=rec
		print >> stderr,filename+":",linc,"lines (not including header)"
		ofil.close()


		
			
	
