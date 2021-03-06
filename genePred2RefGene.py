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

#Usage: convertToRefGene.py genScan.txt startpos=0

import sys;

def main():
	if(len(sys.argv)<2):
		print >>sys.stderr, "convertToRefGene.py genScan.txt name_startpos=0";
		return;
	
	startpos=0;

	if(len(sys.argv)>2):
		startpos=int(sys.argv[2]);
		
	fil=open(sys.argv[1]);
	lino=0;

	for line in fil:
		lino+=1;	
		
		if(lino%(100)==1):
			print >>sys.stderr, "processing line "+str(lino);
		
		items=line.split("\t");
		itemCount=len(items);
		items[itemCount-1]=items[itemCount-1].strip();
		print >>sys.stdout, str(-1)+"\t", #bin
		print >>sys.stdout, "\t".join(items[startpos:]), #name:exonEnds
		print >>sys.stdout,"\t",
		print >>sys.stdout,str(0), #id	
		#if(itemCount==11+startpos):	
		print >>sys.stdout,"\t",
		print >>sys.stdout,items[startpos], #name2 = name
		print >>sys.stdout,"\t",
		print >>sys.stdout,'cmpl', #cdsStartStat
		print >>sys.stdout,"\t",
		print >>sys.stdout,'cmpl', #cdsEndStat
		print >>sys.stdout,"\t",  
		exonCount=int(items[startpos+7]);
		cdsStart=int(items[startpos+5]);
		cdsEnd=int(items[startpos+6]);
		
		exonStartsStr=items[startpos+8].split(',');
		exonEndsStr=items[startpos+9].split(',');
		exonStart=[];
		exonEnd=[];
		#print >> sys.stderr, items[7]+"\n"+items[8];
		#print >> sys.stderr, "exonCount="+str(exonCount)+" size of exonStartsStr="+str(len(exonStartsStr))+ " size of exonEndsStr="+str(len(exonEndsStr));
		for i in range(exonCount):
			exonStart.append(int(exonStartsStr[i]));
			exonEnd.append(int(exonEndsStr[i]));


		strand=items[startpos+2]; #strand
		simExonFrames=[];
		startexon=0;
		if(strand=='+'):
			for i in range(exonCount):
				if (exonEnd[i]<cdsStart or exonStart[i]>cdsEnd):
					simExonFrames.append("-1");
				elif( cdsStart>=exonStart[i] and cdsStart<=exonEnd[i]):
					simExonFrames.append("0");
					startexon=i;
				elif(startexon==i-1):
					frame=(exonEnd[i-1]-cdsStart)%3;
					simExonFrames.append(str(frame));
				else:
					frame=(exonEnd[i-1]-exonStart[i-1]+int(simExonFrames[i-1]))%3;
					simExonFrames.append(str(frame));
		else:
			for i in range(exonCount):
				ind=exonCount-i-1;
				if (exonEnd[ind]<cdsStart or exonStart[ind]>cdsEnd):
					simExonFrames.append("-1");
				elif (cdsEnd>=exonStart[ind] and cdsEnd<=exonEnd[ind]):
					simExonFrames.append("0");
					startexon=i;
				elif(startexon==i-1):
					frame=(cdsEnd-exonStart[ind+1])%3;
					simExonFrames.append(str(frame));
				else:
					frame=(exonEnd[ind+1]-exonStart[ind+1]+int(simExonFrames[i-1]))%3;
					simExonFrames.append(str(frame));
			simExonFrames.reverse();
				


		
		print >>sys.stdout,",".join(simExonFrames)+","; #exonFrames

	print >>sys.stderr, str(lino) +" total lines processed";
	fil.close();

main();
