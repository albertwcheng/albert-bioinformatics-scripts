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

from pylab import *;
from math import log;
from math import fabs;
from sys import argv,stderr,stdout,exit;
from albertcommon import *

import warnings
warnings.simplefilter("ignore",DeprecationWarning)
from getopt import getopt
from scipy.stats import pearsonr,spearmanr

#plotScatter(filename,plotName,startRow,XCol,YCol,XLabel,YLabel,outImage,figformat)

def plotScatter(filename,plotName,startRow1,GCol,RCol,GLabel,RLabel,outFileFigureRG,formatFigure,logb,absvalues):
	
	
	lino=0;

	
	
	RValues=[];
	GValues=[];
	#RLabel="Y";
	#GLabel="X";
	#if(useSmartName):
	#	#use the first line
	#	line=fin.readline();
	#	line=line.strip();
	#	spliton=line.split("\t");
	#	RLabel=spliton[RCol];
	#	GLabel=spliton[GCol];

	#	plotName=spliton[RCol]+" vs "+spliton[GCol];

		
	#	plotNameLessFancy=spliton[RCol]+"-"+spliton[GCol];
	#	outFileFigureRG+=plotNameLessFancy+"."+formatFigure;		
	#	fin.close();
	#	fin=open(filename);
	


	minR="";
	maxR="";
	minG="";
	maxG="";
	fin=open(filename)
	
	for line in fin:
		lino+=1;
			
		line=line.strip();
		spliton=line.split("\t");
		
		lineOut="";		
		

		if(lino<startRow1):	
			continue; #not neccessary?						
		else:
			if spliton[RCol]=="nan" or spliton[GCol]=="nan":
				continue

			RValue=float(spliton[RCol]);
			GValue=float(spliton[GCol]);

			if absvalues:
				RValue=fabs(RValue)
				GValue=fabs(GValue)

			#print >> stderr, "Read",RValue,GValue
			
			if logb!=0:
				try:
					RValue=log(RValue)/logb
				except:
					pass
				try:				
					GValue=log(GValue)/logb			
				except:
					pass
			logRValue=RValue;
			logGValue=GValue;

			firstData=(len(RValues)==0)
			if(firstData or logRValue<minR ):
				minR=logRValue;
			if(firstData or logGValue<minG ):
				minG=logGValue;
			if(firstData or logRValue>maxR ):
				maxR=logRValue;
			if(firstData or logGValue>maxG ):
				maxG=logGValue;
			
			RValues.append(logRValue);
			GValues.append(logGValue);		
	
	#print len(RValues);
	#print len(GValues);
#RG plot
	figure();
	scatter(GValues,RValues,marker='o',color='blue',s=3);
	title(plotName);
	xlabel(GLabel);
	ylabel(RLabel);

	limx=max(fabs(minG),fabs(maxG));
	limy=max(fabs(minR),fabs(maxR));
	lim=max(limx,limy);

	#xminSet=-lim
	#xmaxSet=lim
	#yminSet=-lim
	#ymaxSet=lim

	xminSet=minG
	xmaxSet=maxG
	yminSet=minR
	ymaxSet=maxR

	
	t=linspace(xminSet,xmaxSet,50)
	(slope,yintercept)=polyfit(GValues,RValues,1)
	xr=polyval([slope,yintercept],t)

		
	if slope > 0.5:
		y2=polyval([1,yintercept],t)
		plot(t,y2,'g-.')
	elif slope < -0.5:
		y2=polyval([-1,yintercept],t)
		plot(t,y2,'g-.')	
		
	equstr="\n"
	if yintercept>0:
	 	equstr+="%s=%.2f%s+%.2f" %(RLabel,slope,GLabel,yintercept)
	elif yintercept==0:
		equstr+="%s=%.2f%s" %(RLabel,slope,GLabel)
	else:
		equstr+="%s=%.2f%s%.2f" %(RLabel,slope,GLabel,yintercept)
	
	pearsonR=pearsonr(GValues,RValues)
	spearmanR=spearmanr(GValues,RValues)

	equstr+="\nPearson R^2=%.2f (r=%.2f p-value=%.2f)" %(pearsonR[0]*pearsonR[0],pearsonR[0],pearsonR[1])
	equstr+="\nSpearman R^2=%.2f (r=%.2f p-value=%.2f)" %(spearmanR[0]*spearmanR[0],spearmanR[0],spearmanR[1])
	
	print >> stderr, "Fit:"
	print >> stderr, equstr
	
	text(xminSet,ymaxSet,equstr,verticalalignment="top",horizontalalignment="left",color='red')
	#text(xmaxSet*0.9+2,ymaxSet*0.9,equstr,verticalalignment="top",horizontalalignment="right")
	plot(t,xr,'r-')

	xlim(xmin=xminSet,xmax=xmaxSet);
	ylim(ymin=yminSet,ymax=ymaxSet);
	#xlim(xmin=5,xmax=lim);
	#ylim(ymin=5,ymax=lim);

	#axhline(xmin=-50,xmax=50,color='blue');
	#axhline(y=1,xmin=-50,xmax=50,color='red');
	#axhline(y=-1,xmin=-50,xmax=50,color='green');

	savefig(outFileFigureRG,format=formatFigure);


	#show();

	fin.close();
	#fout.close();

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] filename XCol YCol"
	print >> stderr,"options:"
	print >> stderr,"startRow"
	print >> stderr,"headerRow"
	print >> stderr,"useSmartName use Xlabel and Ylabel in header"
	print >> stderr,"plotName specify plot Name [default is the clean version of input filename]"
	print >> stderr,"figFormat"
	print >> stderr,"outImage outputImageFileName"
	print >> stderr,"logtransform base"
	print >> stderr,"abs plot absolute values"
	explainColumns(stderr)
	exit()

if __name__=='__main__':
	programName=argv[0]
	useSmartName=False
	startRow=2
	headerRow=-1
	fs="\t"
	figformat="png"
	plotName=""
	outImage=""
	logb=0
	absvalues=False
	opts,args=getopt(argv[1:],'',['startRow=','headerRow=','useSmartName','plotName=','figFormat=','outImage=','logtransform=','abs'])

	for o,v in opts:
		if o=='--startRow':
			startRow=int(v)
		elif o=='--headerRow':
			headerRow=int(v)
		elif o=='--useSmartName':
			useSmartName=True
		elif o=='--plotName':
			plotName=v
		elif o=='--figFormat':
			figformat=v
		elif o=='--outImage':
			outImage=v
		elif o=='--logtransform':
			logb=log(float(v))
		elif o=='--abs':
			absvalues=True
	try:
		filename,XCol,YCol=args
	except:
		printUsageAndExit(programName)
#if(len(argv)<9 ):
#	print >> sys.stderr,"Usage: "+argv[0]+" filename,plotName,startRow1,RCol1,GCol1,outFileFigureRG,formatFigure,useSmartName=y|n";
	if headerRow==-1:
		headerRow=startRow-1	

	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	XCol=getCol0ListFromCol1ListStringAdv(header,XCol)[0]
	YCol=getCol0ListFromCol1ListStringAdv(header,YCol)[0]
	XLabel='X'
	YLabel='Y'
	if useSmartName:
		XLabel=header[XCol]
		YLabel=header[YCol]
	
	if plotName=="":
		plotName=cleanfilename(filename)

	if outImage=="":
		outImage=plotName+"."+figformat
	
		
	plotScatter(filename,plotName,startRow,XCol,YCol,XLabel,YLabel,outImage,figformat,logb,absvalues)


