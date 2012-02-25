#!/usr/bin/env python

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
from os.path import basename
from drawVenn import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] file1[=relabel1] file2[=relabel2] ... > outfile (a union of all lines with their counts in each file"
	print >> stderr, "Options:"
	print >> stderr,"--headerFrom1To n  use row 1 to row n of file 1 as header , do not compare these lines in all files, just directly output to each output files"	
	print >> stderr,"--outcombination fileprefix,filesuffix"
	print >> stderr,"--suppress-stat no printing membership table to stdout"
	#print >> stderr,"--remove-ext-on-stdout-labels remove the file extension on stdout header labels for filenames"
	print >> stderr,"--name-content label   give the non-headed content a label"
	print >> stderr,"--maxcountTo1  make counts into 1: with line, 0: without line"
	print >> stderr,"--usebasename use basename of filenames as label and outcombination infices"
	print >> stderr,"--remove-ext remove the file extension as label and outcombination infice"
	print >> stderr,"--draw-venn draw venn report for 3 files (3-venn) or 2 files(2-venn). Other number of files not supported"
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

def removeExtension(filename):
	return ".".join(filename.split(".")[:-1])


if __name__=='__main__':
	programName=argv[0]
	headerFrom1To=-1
	outcombination=["",""]
	maxcountTo1=False
	stdoutPrint=True
	removeExtensionOnStdOut=False
	fs="\t"
	contentName="content"
	useBaseName=False
	drawVenns=False
	
	
	try:
		#'remove-ext-on-stdout-labels',
		opts,args=getopt(argv[1:],'',['headerFrom1To=','outcombination=','suppress-stat','name-content=','maxcountTo1','usebasename','remove-ext','draw-venn'])
		for o,v in opts:
			if o=='--headerFrom1To':
				headerFrom1To=int(v)
			elif o=='--outcombination':
				outcombination=v.split(",")
			elif o=='--suppress-stat':
				stdoutPrint=False
			elif o=='--remove-ext':
				removeExtensionOnStdOut=True
			elif o=='--name-content':
				contentName=v
			elif o=='--maxcountTo1':
				maxcountTo1=True
			elif o=='--usebasename':
				useBaseName=True
			elif o=='--draw-venn':
				drawVenns=True

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
	
	
	if numfiles<2 or numfiles>3:
		if drawVenns:
			print >> stderr,"drawvenn not supported for file number <2 or >3. abort"
			exit(1)
	
	labels=[]
	
	for i in range(0,len(filenames)):
		if "=" in filenames[i]:
			filenames[i],relab=filenames[i].split("=")
			labels.append(relab)
		else:
			relab=filenames[i]
			if removeExtensionOnStdOut:
				relab=removeExtension(relab)
		
			if useBaseName:
				relab=basename(relab)
			
			labels.append(relab)
			
			

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
	

	

	if stdoutPrint:
	
		if len(header)>0:
			for headerline in header: 
				print >> stdout, headerline.rstrip("\r\n")+fs+(fs.join(labels)) ###???
		else:
			print >> stdout,contentName+fs+fs.join(labels)
				
	basenames=[]

	for lin,counter in line_count.items():
		fillListInPlace(counter,numfiles,0)
		if "".join(outcombination)!="" or drawVenns:

			ofilename=outcombination[0]+("_".join(getSubvectorGe1(labels,counter)))+outcombination[1]
			
			if ofilename not in ofilehandles:
				#print >> stdout,"opening ofile=",ofilename
				if "".join(outcombination)!="":
					ofil=open(ofilename,"w")
					if len(header)>0:
						ofil.writelines(header)
				else:
					ofil=None
					
				ofilehandles[ofilename]=[ofil,0]
				linc=0
			else:
				ofil,linc=ofilehandles[ofilename]
			
			if ofil:
				ofil.write(lin)
			ofilehandles[ofilename][1]=linc+1
		if stdoutPrint:
			print >> stdout,lin.rstrip("\r\n")+fs+(fs.join(toStrVector(counter)))

	#print >> stderr,line_count	
			
	#now close all openfiles
	for filename,rec in ofilehandles.items():
		ofil,linc=rec
		
		if ofil:
			print >> stderr,filename+":",linc,"lines (not including header)"
			ofil.close()

	if drawVenns:
		if len(labels)==2:
			a_name=outcombination[0]+("_".join(getSubvector(labels,[0],True)))+outcombination[1]
			b_name=outcombination[0]+("_".join(getSubvector(labels,[1],True)))+outcombination[1]
			a_b_name=outcombination[0]+("_".join(getSubvector(labels,[0,1],True)))+outcombination[1]
			try:
				a_only_num=ofilehandles[a_name][1]
			except:
				a_only_num=0
			try:
				b_only_num=ofilehandles[b_name][1]
			except:
				b_only_num=0
			try:
				a_b_num=ofilehandles[a_b_name][1]
			except:
				a_b_num=0
				
			a_num=a_only_num+a_b_num
			b_num=b_only_num+a_b_num
			
			drawTwoVenn(a_num,b_num,a_b_num,300,200,outcombination[0]+labels[0]+"_"+labels[1]+".venn.png",labels[0]+" and "+labels[1],[labels[0],labels[1]],True,[[255,0,0],[0,0,255]],outcombination[0]+labels[0]+"_"+labels[1]+".venn.htm")
		elif len(labels)==3:
			print >> stderr,"Warning:3-venn can give unknown strange result"
			a_name=outcombination[0]+("_".join(getSubvector(labels,[0],True)))+outcombination[1]
			b_name=outcombination[0]+("_".join(getSubvector(labels,[1],True)))+outcombination[1]
			c_name=outcombination[0]+("_".join(getSubvector(labels,[2],True)))+outcombination[1]
			a_b_name=outcombination[0]+("_".join(getSubvector(labels,[0,1],True)))+outcombination[1]
			a_c_name=outcombination[0]+("_".join(getSubvector(labels,[0,2],True)))+outcombination[1]
			b_c_name=outcombination[0]+("_".join(getSubvector(labels,[1,2],True)))+outcombination[1]
			a_b_c_name=outcombination[0]+("_".join(getSubvector(labels,[0,1,2],True)))+outcombination[1]
			try:
				a_only_num=ofilehandles[a_name][1]
			except:
				a_only_num=0
			try:
				b_only_num=ofilehandles[b_name][1]
			except:
				b_only_num=0
			try:
				c_only_num=ofilehandles[c_name][1]
			except:
				c_only_num=0				
			try:
				a_b_num=ofilehandles[a_b_name][1]
			except:
				a_b_num=0
			try:
				a_c_num=ofilehandles[a_c_name][1]
			except:
				a_c_num=0
			try:
				b_c_num=ofilehandles[b_c_name][1]
			except:
				b_c_num=0	
			try:
				a_b_c_num=ofilehandles[a_b_c_name][1]
			except:
				a_b_c_num=0	
			#print >> stderr,a_only_num+a_b_num+a_c_num+a_b_c_num,b_only_num+a_b_num+b_c_num+a_b_c_num,c_only_num+a_c_num+b_c_num+a_b_c_num,a_b_num+a_b_c_num,a_c_num+a_b_c_num,b_c_num+a_b_c_num,a_b_c_num	
			drawThreeVenn(a_only_num+a_b_num+a_c_num+a_b_c_num,b_only_num+a_b_num+b_c_num+a_b_c_num,c_only_num+a_c_num+b_c_num+a_b_c_num,a_b_num+a_b_c_num,a_c_num+a_b_c_num,b_c_num+a_b_c_num,a_b_c_num,300,200,outcombination[0]+labels[0]+"_"+labels[1]+"_"+labels[2]+".venn.png",labels[0]+" and "+labels[1]+" and "+labels[2],[labels[0],labels[1],labels[2]],True,[[255,0,0],[0,0,255],[0,255,0]],outcombination[0]+labels[0]+"_"+labels[1]+"_"+labels[2]+".venn.htm")