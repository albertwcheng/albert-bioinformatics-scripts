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

'''
[BFUE]>colStat.py BFUE.chr1.exinc.xls 
[:::::                  R 1                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       Alt3UTR
2                       B                       2310028N02Rik
3                       C                       2310028N02Rik:1
4                       D                       chr1:193173730+,chr1:193174080+,chr1:193174795+
5                       E                       chr1
6                       F                       +
7                       G                       2
8                       H                       193173730-193174080/193174081-193174795
9                       I                       193173730
10                      J                       193174795
11                      K                       =HYPERLINK(http://genome.ucsc.edu/cgi-bin/hgTracks?db=mm9&acembly=full&mgcGenes=hide&genscan=dense&ensGene=hide&xenoRefGene=hide&mrna=hide&refGene=hide&position=chr1:193173730-193174795,UCSC Browse)
12                      L                       351
13                      M                       62
14                      N                       1031
15                      O                       221
16                      P                       351:62;680:159
17                      Q                       11:351:62;01:1031:221
18                      R                       0.056675;0.943325

to 

myGene.isoforms

{"gene_id": "U2AF1",
 "exons": [88, 67, 67, 50],
 "isoforms": [[1, 2, 4], [1, 3, 4], [1, 2, 3, 4]]}

myGene.reads

num_reads	read_type
8		[1,0,0]
1		[0,1,0]
5	[0,0,1]
34	[1,1,0]
46	[0,1,1]
33	[1,1,1]

'''
COL_CHR=5 - 1
COL_STRAND=6 - 1
COL_BOUND=8 - 1
COL_MISO=17 - 1
COL_ID=3 - 1
DIR_NAME="MISO_input"
IGNORE_SINGLETON=True

from sys import *
from os import mkdir
from os.path import isdir
from shutil import rmtree
import simplejson as json
from getopt import getopt

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['add-readlength=','out-dir='])
	addReadLength=0

	try:
		filenames=args
	except:
		print >> stderr,programName,"[--add-readlength <readlength> --out-dir path] <filenames...>"
		exit()
	
	if len(filenames)==0:
		print >> stderr,"no files specified"
		print >> stderr,programName,"filenames"
		exit()

	for o,v in opts:
		if o=='--add-readlength':
			addReadLength=int(v)
		elif o=='--out-dir':
			DIR_NAME=v


	#first of all, empty an output file dir
	if isdir(DIR_NAME):
		rmtree(DIR_NAME)

	mkdir(DIR_NAME)

	for filename in filenames:
		fil=open(filename)
		print >> stderr,"processing file",filename
		for lin in fil:
			fields=lin.strip().split("\t")
			MISOString=fields[COL_MISO]
			ID=fields[COL_ID]
			strand=fields[COL_STRAND]
			bounds=fields[COL_BOUND]
			chrom=fields[COL_CHR]
			#now split
			IsoformInfoStrings=MISOString.split(";")
			numIsoforms=len(IsoformInfoStrings)
			bounds=bounds.split("/")
			#if strand=='-':
				#bounds.reverse()
			fragmentlengths=[]

			for bound in bounds:
				start,end=bound.split("-")
				fragmentlength=int(end)-int(start)+1
				
				if fragmentlength<=0:
					print >> stderr,"fragmentlength<=0:",fields
					exit()

				fragmentlengths.append(fragmentlength)


			for i in range(0,len(IsoformInfoStrings)):
				IsoformInfoStrings[i]=IsoformInfoStrings[i].split(":")

			if IGNORE_SINGLETON and numIsoforms==1:
				continue
			
			isoformStruct=dict()
			isoformStruct["gene_id"]=ID
			if addReadLength==0:
				isoformStruct["exons"]=fragmentlengths
			else:
				RLA_fragmentlengths=[]				
				isoformStruct["exons"]=RLA_fragmentlengths
				for fragmentlength in fragmentlengths:
					RLA_fragmentlengths.append(fragmentlength+addReadLength)
				###RLA_fragmentlengths[-1]-=addReadLength #not the terminal one

			isoformList=[]
			isoformStruct["isoforms"]=isoformList
			nonuniqList=[]
			isoformStruct["uniqueness"]=nonuniqList
			CUMP=[]
			isoformStruct["cump"]=CUMP
			CUMLENGTH=[]
			#CUMP=[]
			#isoformStruct["cump"]=CUMP
			isoformStruct["chr"]=chrom
			isoformStruct["creal_exons"]=CUMLENGTH
			isoformStruct["strand"]=strand
			isoformStruct["bounds"]=bounds
			UMP=[]
			isoformStruct["ump"]=UMP
			isoformStruct["misostring"]=MISOString
			isoformStruct["readLengthAdded"]=addReadLength
			#REAL_EXONS=[]
			isoformStruct["real_exons"]=fragmentlengths

			foutIsoforms=open(DIR_NAME+"/"+ID+".isoforms","w")
			foutReads=open(DIR_NAME+"/"+ID+".reads","w")
			print >> foutReads,"num_reads\tread_type"
			indx=0
			previsoformpos=0
			cumlength=0
			for binvector,isoformpos,isoformreads in IsoformInfoStrings:
				indx+=1
				fragmentlength=fragmentlengths[indx-1]
				cumlength+=fragmentlength				
				isoformpos=int(isoformpos)
				if isoformpos<0:
					print >> stderr,"isoformpos<0:",fields
					exit()
				CUMLENGTH.append(cumlength)
				CUMP.append(isoformpos)
				thisUMP=isoformpos-previsoformpos
				if thisUMP<0:
					print >> stderr,"ump<=0:",fields
					exit()
				UMP.append(thisUMP)
				nonuniqpos=max(0,fragmentlength-thisUMP)
				#if nonuniqpos<0:
				#	print >> stderr,"nonuniq<0:",fields
				#	exit()	
				nonuniqList.append(nonuniqpos)

				isoformreads=int(isoformreads)
				binvectorstring="["+(",".join(list(binvector)))+"]"
				isoformList.append(range(1,indx+1))
				previsoformpos=isoformpos
				#print >> foutIsoforms,ID+":"+str(indx)+"\t"+str(isoformpos)
				print >> foutReads,str(isoformreads)+"\t"+binvectorstring			
			
			json.dump(isoformStruct,foutIsoforms)
				
			foutIsoforms.close()
			foutReads.close()
		fil.close()

	
