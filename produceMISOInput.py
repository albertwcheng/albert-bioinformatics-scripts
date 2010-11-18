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


#isoform_ids  length
isoform1_id  1000
isoform2_id  6000

myGene.reads


#number_of_reads  read_alignment_type
30   [1, 1, 0]


'''


COL_MISO=17 - 1
COL_ID=3 - 1
DIR_NAME="MISO_input"
IGNORE_SINGLETON=True

from sys import *
from os import mkdir
from os.path import isdir
from shutil import rmtree

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filenames=args
	except:
		print >> stderr,programName,"filenames"
		exit()

	if len(filenames)==0:
		print >> stderr,"no files specified"
		print >> stderr,programName,"filenames"
		exit()

	
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
			
			#now split
			IsoformInfoStrings=MISOString.split(";")
			numIsoforms=len(IsoformInfoStrings)

			for i in range(0,len(IsoformInfoStrings)):
				IsoformInfoStrings[i]=IsoformInfoStrings[i].split(":")

			if IGNORE_SINGLETON and numIsoforms==1:
				continue
			
		
			foutIsoforms=open(DIR_NAME+"/"+ID+".isoforms","w")
			foutReads=open(DIR_NAME+"/"+ID+".reads","w")
			indx=0
			for binvector,isoformpos,isoformreads in IsoformInfoStrings:
				indx+=1				
				isoformpos=int(isoformpos)
				isoformreads=int(isoformreads)
				binvectorstring="["+(", ".join(list(binvector)))+"]"
				print >> foutIsoforms,ID+":"+str(indx)+"\t"+str(isoformpos)
				print >> foutReads,str(isoformreads)+"\t"+binvectorstring			

			foutIsoforms.close()
			foutReads.close()
		fil.close()

	
