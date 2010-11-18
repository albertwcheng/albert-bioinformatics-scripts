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

#chr7:5,533,305-5,536,758
#X8065_72:6:138:433:500  chr7    62907   -       0       0       19      19      
#19      0       0       1       6       39      agcgtgggaGGAGCCAGTGTGAGGCAGGGGCT
#CACACCT 11/1%5553<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

import sys;
from sys import stdout,stderr;
from math import log;
from math import sqrt;
import numpy;
from getopt import getopt

def mean(A):
	return numpy.mean(A);

def stdev(A):

	N=len(A);
	if N<=1:
		return 0;
	return numpy.std(A)*sqrt(float(N)/(N-1));

programName=sys.argv[0]
opts,args=getopt(sys.argv[1:],"",["threshold=","colors=","logbase=","tracknames="])

if len(args)!=5:
	print >> stderr,"Usage:",args[0]," fileMAQ,... chr from to binInterval"
	print >> stderr,"Options:"
	print >> stderr,"threshold  set the threshold to show default: 0"
	print >> stderr,"colors r,g,b_r,g,b_... default:0,0,0 (black)"
	print >> stderr,"logbase  default: 2"
	print >> stderr,"tracknames name1,..."
	exit();

threshold=0
colors=[]
logbase=2
nameTrack=[]


for a,v in opts:
	if a=="--threshold":
		threshold=float(v)
	elif a=="--colors":
		colors=v.split("_")
	elif a=="--logbase":
		logbase=float(v)
	elif a=="--tracknames":
		nameTrack=v.split(",")
		

threshold=log(threshold)/log(logbase)




fileMAQ,chrom,from1,to1,binInterval=args;

fileMAQ=fileMAQ.split(",")

if len(nameTrack)<1:
	nameTrack=fileMAQ

while len(colors)<len(fileMAQ):
	colors.append("0,0,0")

def fillInBlockStat(blockStat,VALUE,start,endEx):
	blockSizeMax=endEx-start;
	for bs in range(1,blockSizeMax+1):
		if not blockStat.has_key(bs):
			blockStat[bs]=dict();
			blockStat[bs]["values"]=[];
		for i in range(start,endEx,bs):
			csum=0;			
			for j in range(start,start+bs):
				csum+=VALUE[j];
			blockStat[bs]["values"].append(csum);

def needBinKey(binKey,CHR,POS,VALUE,chrom,from1,binInterval,valueToSet):
	while len(CHR)<binKey+1:
		CHR.append(chrom)
		POS.append(from1+binKey*binInterval)
		VALUE.append(valueToSet)

def getWig(fileMAQ,nameTrack,chrom,from1,to1,binInterval,color,threshold,logbase):
	from1=int(from1.replace(",",""));
	to1=int(to1.replace(",",""));
	binInterval=int(binInterval);

	fin=open(fileMAQ);
	logb=log(logbase)
	CHR=[];
	POS=[];
	VALUE=[];
	#create bin:
	end1=to1+binInterval;

	#for pos in range(from1,end1,binInterval):
	#	CHR.append(chrom);
	#	POS.append(pos);
	#	VALUE.append(0);


	for lin in fin:
		lin=lin.rstrip("\r\n");
		spliton=lin.split("\t");
	
		position=int(spliton[2]);
	
		if ((from1<=0 or position>=from1) and (to1<=0 or position<=to1)):
			binKey=int((position-from1)/binInterval);
			needBinKey(binKey,CHR,POS,VALUE,chrom,from1,binInterval,0)
			VALUE[binKey]+=1;



	#now output:
	print >> stdout,"browser position",chrom+":"+str(from1)+"-"+str(to1);
	print >> stdout, "browser hide all";
	print >> stdout,"browser full acembly knownGene"
	print >> stdout,'track type=wiggle_0 name="'+nameTrack+'" description="Log2 Read Counts for '+nameTrack+'" visibility=full color='+color+' priority=20';

	for binKey in range(0,len(VALUE)):
		vlog=0;
		if(VALUE[binKey]>0):
			vlog=log(VALUE[binKey])/logb;

		if vlog<threshold:
			continue
	
		print >> stdout,chrom,POS[binKey],POS[binKey]+binInterval-1,vlog;

	#now go through the window, get window of more than 3 blocks, get middle blocks and calculate

	stage=0;

	blockStat=dict();
	binKeyE=0;

	for binKey in range(0,len(VALUE)):
		binKeyE=binKey;		
		value=VALUE[binKey];
		if(value==0):
			#break a chain
			if stage>=4:
				#now can do the cal
				fillInBlockStat(blockStat,VALUE,binKey-stage+2,binKey-1);
			stage=0;
		else:
			stage+=1;
				
	if stage>=4:
		fillInBlockStat(blockStat,VALUE,binKeyE-stage+1,binKeyE);
		#now do the cal:

	#now print the stats:
	for blockKey in blockStat.keys():
		vals=blockStat[blockKey]["values"];
		m=mean(vals);
		s=stdev(vals);
		cv=float(s)/m;
		print >> stdout,"#\t",blockKey*binInterval,"\t",m,"\t",s,"\t",cv;

print >> stderr, "files=",fileMAQ
print >> stderr, "name Tracks=",nameTrack
print >> stderr, "range=",chrom,":",from1,"-",to1

for filemaq,nametrack,color in zip(fileMAQ,nameTrack,colors):
	getWig(filemaq,nametrack,chrom,from1,to1,binInterval,color,threshold,logbase)
#fileMAQ,nameTrack,chrom,from1,to1,binInterval,color,threshold,logbase):

#browser position chr19:59302001-59311000
#browser hide all
#browser pack refGene encodeRegions
#browser full altGraph
#	300 base wide bar graph, autoScale is on by default == graphing
#	limits will dynamically change to always show full range of data
#	in viewing window, priority = 20 positions this as the second graph
#	Note, zero-relative, half-open coordinate system in use for bed format
#track type=wiggle_0 name="Bed Format" description="BED format" \
#    visibility=full color=200,100,0 altColor=0,100,200 priority=20
#chr19 59302000 59302300 -1.0
#chr19 59302300 59302600 -0.75
#chr19 59302600 59302900 -0.50
#chr19 59302900 59303200 -0.25
#chr19 59303200 59303500 0.0
#chr19 59303500 59303800 0.25
#chr19 59303800 59304100 0.50
#chr19 59304100 59304400 0.75
#chr19 59304400 59304700 1.00
#	150 base wide bar graph at arbitrarily spaced positions,
#	threshold line drawn at y=11.76
#	autoScale off viewing range set to [0:25]
#	priority = 10 positions this as the first graph
#	Note, one-relative coordinate system in use for this format

