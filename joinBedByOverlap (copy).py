#!/usr/bin/python

'''

Join Bed File rows if they are overlapped. Requires simpleBedOverlap.py

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


from simpleBedOverlap import *
from sys import *
from getopt import getopt

def printUsageAndExit(programName):
	print >> stderr,programName,"[option] bedfile1 bedfile2 > outbed"
	print >> stderr,"Options:"
	print >> stderr,"--min-overlap length"
	print >> stderr,"--print-only-bed2"
	print >> stderr,"--add-chrom-if-needed"

	exit()

def lengthOfBound(coord):
	return max([0,coord[1]-coord[0]])


def joinIntervalsByBins(bin1,bin2,bed1,bed2,overlapLength,addChromIfNeeded):
	#foreach of Bed1 chr
	newBed=dict()
	em=[]
	for bin1Chr,bin1ChromDict in bin1.items():
		print >> stderr,"processing bin1chr",bin1Chr,
		try:		
			bin2ChromDict=bin2[bin1Chr]
			bin2Chr=bin1Chr
		except:
			if addChromIfNeeded:
				bin2haschr=(bin2.keys()[0][0:3].lower()=='chr')
				bin1haschr=(bin1Chr[0:3].lower()=='chr')
				if (bin1haschr or bin2haschr) and (not (bin1haschr and bin2haschr)): #inconsistent chr label
					if bin1haschr:
						bin2Chr=bin1Chr[3:]
					else:
						bin2Chr=bin2.keys()[0][0:3]+bin1Chr
					
					try: #now try again:
						bin2ChromDict=bin2[bin2Chr]
					except:
						continue
				else:
					continue
			else:
				continue
		
		bed1ChromDict=bed1[bin1Chr]
		bed2ChromDict=bed2[bin2Chr] ##supposed to be the same as bin1Chr, but can differ

		#for each bin in bin1
		for bkey1,b1 in bin1ChromDict.items():
			try:
				b2=bin2ChromDict[bkey1]
			except:
				continue
			
			#now pairwise bruteforce in each bin set
			for coord1 in b1:
				for coord2 in b2:		
					ob=overlapBound(coord1,coord2)
					
					if isValid(ob) and lengthOfBound(ob)>=overlapLength:
						newBed[(bin1Chr,coord1[0],coord1[1],coord2[0],coord2[1])]=(bed1ChromDict[coord1],bed2ChromDict[coord2],ob)
						#addBedEntry(newBed,bin1Chr,ob[0],ob[1],bed1ChromDict[coord1]+bed2ChromDict[coord2]+list(coord1)+list(coord2))

	return newBed


if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['min-overlap=','print-only-bed2','add-chrom-if-needed'])
	
	try:
		bedfile1,bedfile2=args
	except:
		printUsageAndExit(programName)

	binInterval=100000
	
	overlapLength=1
	onlyBed2=False
	addChromIfNeeded=False
	
	for o,v in opts:
		if o=='--min-overlap':
			overlapLength=int(v)
		elif o=='--print-only-bed2':
			onlyBed2=True
		elif o=='--add-chrom-if-needed':
			addChromIfNeeded=True

	print >> stderr,"reading in",bedfile1
	bed1=readBed(bedfile1)
	print >> stderr,"reading in",bedfile2
	bed2=readBed(bedfile2)
	print >> stderr,"making bins"
	bin1=binIntv(bed1,binInterval)
	#print >> stderr,bin1
	bin2=binIntv(bed2,binInterval)
	#print >> stderr,bin2
	print >> stderr,"join by overlap...",
	
	jbed=joinIntervalsByBins(bin1,bin2,bed1,bed2,overlapLength,addChromIfNeeded)
	
	#now print
	print >> stderr,"... done."
	print >> stderr,"printing"
	for bkey,content in jbed.items():
		chrom,coord1start,coord1end,coord2start,coord2end=bkey
		bed1chromdata,bed2chromdata,overlapBound=content
		if onlyBed2:
			print >> stdout,"\t".join([chrom,str(coord2start),str(coord2end)]+bed2chromdata)
		else:			
			print >> stdout,"\t".join([chrom,str(coord1start),str(coord1end)]+bed1chromdata+[chrom,str(coord2start),str(coord2end)]+bed2chromdata)
	

	
	
