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

'''[3UTRdb]>colStat.py TandemUTR.mm9.gff 
[:::::                  R 1                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       chr3
2                       B                       TandemUTR
3                       C                       chr3:14900090:14900578:+;chr3:14900579:14900770:+.core
4                       D                       14900090
5                       E                       14900578
6                       F                       0
7                       G                       +
8                       H                       .
9                       I                       attr

'''

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		print >> stderr,programName,"ericfilename > outputbed"
		exit()


	EricStructForward=dict()   # EricStructForward[chrom][start]=[end,...]
	EricStructReverse=dict()   # EricStructReverse[chrom][end]=[start,...]

	
	fil=open(filename)
	for lin in fil:
		lin=lin.strip()
		fields=lin.split("\t")
		chrom=fields[0]
		strand=fields[6]
		start=int(fields[3])
		end=int(fields[4])
		isForward=(strand=="+")

		if isForward:
			try:
				EricStructChrom=EricStructForward[chrom]
			except:
				EricStructChrom=dict()
				EricStructForward[chrom]=EricStructChrom
			try:
				EricStructChromCoUTR=EricStructChrom[start] ##
			except:
				EricStructChromCoUTR=set()
				EricStructChrom[start]=EricStructChromCoUTR ##

			EricStructChromCoUTR.add(end) ##
 
		else:
			try:
				EricStructChrom=EricStructReverse[chrom]
			except:
				EricStructChrom=dict()
				EricStructReverse[chrom]=EricStructChrom

			try:
				EricStructChromCoUTR=EricStructChrom[end] ##
			except:
				EricStructChromCoUTR=set()
				EricStructChrom[end]=EricStructChromCoUTR ##

			EricStructChromCoUTR.add(start) ##

		

				
	fil.close()

	#now the real deal: process

	for chrom,EricStructChrom in EricStructForward.items():
		print >> stderr,"processing forward for chrom",chrom
		for start,ends in EricStructChrom.items():
			ends=list(ends)			
			ends.sort()
			prevEnd=-1
			for end in ends:
				if prevEnd==-1:
					print >> stdout,chrom+"\t"+str(start)+"\t"+str(end)+"\t"+"+"+"\t"+str(start)+"\t"+str(ends[-1])
				else:
					print >> stdout,chrom+"\t"+str(prevEnd)+"\t"+str(end)+"\t"+"+"+"\t"+str(start)+"\t"+str(ends[-1])
				prevEnd=end

	for chrom,EricStructChrom in EricStructReverse.items():
		print >> stderr,"processing reverse for chrom",chrom
		for end,starts in EricStructChrom.items():
			starts=list(starts)
			starts.sort(reverse=True)
			prevStart=-1
			for start in starts:
				if prevStart==-1:
					print >> stdout,chrom+"\t"+str(start)+"\t"+str(end)+"\t"+"-"+"\t"+str(starts[-1])+"\t"+str(end)
				else:
					print >> stdout,chrom+"\t"+str(start)+"\t"+str(prevStart)+"\t"+"-"+"\t"+str(starts[-1])+"\t"+str(end)
				prevStart=start



