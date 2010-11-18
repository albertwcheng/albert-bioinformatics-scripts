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

##
#
#
# version 2: updated 2009-1-4
#  - allows ignoring var BGk, SNR
#
# version 1: updated 2008-12-17

##ZEROEXP=0.00000001

from pylab import *;
from math import log;
from math import fabs;
from sys import argv;
from sys import stderr;
from sys import stdout;
from math import sqrt;
from getopt import getopt;
##from math import max;
from math import ceil;

##def logSafe(x):
##	if x<=0:
##		return -5.8;
##	else:
##		return log(x);


def sumOfRatios(R,G,indices,n):
	t=0;	
	
	if(len(indices)==0):
		for i in range(0,n):
			t+=float(R[i])/G[i];	
	else:
		for i in indices:
			t+=float(R[i])/G[i];
	
	return t;	


#side-effect: indices
#def eliminateOutlierControl(R,G,indices,outlierThr):
#	logOutlierThr=log(outlierThr);
#	for i in indices:
#		t=float(R)/G;
#		if(fabs(log(t))>=logOutlierThr):
#			indices.remove(i);

def polyFitCI99(c):
	LLa=[-5.002,4.462,-3.496,0.9968]; #a3 a2 a1 a0
	ULa=[78.349,-15.161,4.810,0.9648];
	meana=[0.364,1.279,-0.0427,1.001];
	SDa=[6.259,0.190,1.341,0.00225];
	
	return [c,
		LLa[0]*(c**3)+LLa[1]*(c**2)+LLa[2]*(c)+LLa[3],
		ULa[0]*(c**3)+ULa[1]*(c**2)+ULa[2]*(c)+ULa[3],
		meana[0]*(c**3)+meana[1]*(c**2)+meana[2]*(c)+meana[3], 
		SDa[0]*(c**3)+SDa[1]*(c**2)+SDa[2]*(c)+SDa[3]];


def polyFitCI95(c):
	LLa=[-2.805,2.911,-2.706,0.979]; #a3 a2 a1 a0
	ULa=[28.644,-2.830,3.082,0.989];
	meana=[0.364,1.279,-0.0427,1.001];
	SDa=[6.259,0.190,1.341,0.00225];
	
	return [c,
		LLa[0]*(c**3)+LLa[1]*(c**2)+LLa[2]*(c)+LLa[3],
		ULa[0]*(c**3)+ULa[1]*(c**2)+ULa[2]*(c)+ULa[3],
		meana[0]*(c**3)+meana[1]*(c**2)+meana[2]*(c)+meana[3], 
		SDa[0]*(c**3)+SDa[1]*(c**2)+SDa[2]*(c)+SDa[3]];

def normalizedRatioVector(R,G,m,indices,n):
	tps=[];
	sumI=0;
	if(len(indices)==0):
		for i in range(0,n):
			tp=float(R[i])/G[i]/m;
			t_1sq=(tp-1.0)**2;
			tsp1=(1.0+tp**2);
			sumI+=t_1sq/tsp1;
			tps.append(tp);
	else:
		for i in indices:
			tp=float(R[i])/G[i]/m;
			t_1sq=(tp-1.0)**2;
			tsp1=(1.0+tp**2);
			sumI+=t_1sq/tsp1;
			tps.append(tp);
	
	c=sqrt(sumI/n);
	return polyFitCI95(c);
			


def iterationRatioStat(GeneID,R,G,miu,controlGeneIndex,nControlGenes):
#return [m,c,LL,UL,miu,SD], miu the predicted mean of ratios of control genes, m the normalization factor
	##print >> stderr,nControlGenes,miu
	m=sumOfRatios(R,G,controlGeneIndex,nControlGenes)/nControlGenes/miu;
	(c,LL,UL,miu,SD)=normalizedRatioVector(R,G,m,controlGeneIndex,nControlGenes);
	##mLL=LL*m;
	##mUL=UL*m;
	return [m,c,LL,UL,miu,SD];
	

def iterativeRatioStat(GeneID,R,G,initmiu,controlGeneList,maxChangeThrControl,iterationLimit,iterationChangeMin):
	#Gene ID is the vector for gene ID
	#R is the values for R channel not logged
	#G is the values for G channel not logged	

	logMaxChangeThrControl=log(maxChangeThrControl);
	
	controlGeneIndex=[];


	for controlGene in controlGeneList:
		try:

			index=GeneID.index(controlGene);
			logt=log(R[index])-log(G[index]);
			if(fabs(logt)<logMaxChangeThrControl):
				controlGeneIndex.append(index);
			else:
				print >> stderr, "Control Gene", controlGene,"has change > thr";
		except ValueError:
			print >> stderr, "Control Gene",controlGene,"not found in data";
	
	nControlGenes=len(controlGeneIndex);

	if(nControlGenes==0):
		print >> stderr,"No control genes specified/ usable, selecting genes from whole gene list as control";
		# use the whole gene list;
		nWholeList=len(GeneID);
		for index in range(0,nWholeList):
			logt=log(R[index])-log(G[index]);
			if(fabs(logt)<logMaxChangeThrControl):
				controlGeneIndex.append(index);

		nControlGenes=len(controlGeneIndex);

	miu=initmiu;

	iteration=0;

	print >> stderr, "Step\tscaling factor\tc\tmiu\tm";
	for iteration in range(0,iterationLimit):
		prevmiu=miu;	
	
		if(iteration>0):
			prevm=m;
			prevc=c;		
		(m,c,LL,UL,miu,SD)=iterationRatioStat(GeneID,R,G,miu,controlGeneIndex,nControlGenes);		
		
		dmiu=miu-prevmiu;
		if iteration==0:
			print >> stderr,"Initial"+"\t"+"-"+"\t"+"-"+"\t"+str(prevmiu)+"\t"+str(m);
		else:
			print >> stderr, str(iteration+1)+"\t"+str(float(1)/prevm)+"\t"+str(prevc)+"\t"+str(prevmiu)+"\t"+str(prevm);
		if(fabs(dmiu)<iterationChangeMin):
			
			break;
		
	print >> stderr, str(iteration+2)+"\t"+str(float(1)/m)+"\t"+str(c)+"\t"+str(miu)+"\t"+str(m);	
	
	return (m,c,LL,UL,miu,SD);


def loadList(filename):
	
	L=[];	
	
	try:
		fin=open(filename);
		for line in fin:
			line=line.strip();
			if(line=="_end_"):
				break;		
			L.append(line);

		fin.close();	
	except IOError:
		print >> stderr, filename,"not openable, use whole list";
	
	return L;


def drawGeneByName(GeneID,X,Y,geneName,display,color):
	try:
		if(len(geneName)<1):
			return;

		#if(geneName[len(geneName)-1]!=','):
		#	geneName+=",";

		if(display==""):
			display=geneName; #.split(",")[0];

		inx=GeneID.index(geneName);
		plot((X[inx],),(Y[inx],),color+'o');
		text(X[inx],Y[inx],display,{'color' : color});
		print >> stderr, geneName, "[",X[inx],Y[inx],"]";
	except ValueError:
		print >> stderr, geneName, " not found, not texted";


def mean(x,y):
	return (x+y)/2

#side-effect: fill-up SNR,M,A, and newR (normalized), lognewR, logG;
#returns: [minSNR,maxSNR]
def FillUpSNR(SNR,M,A,newR,lognewR,logG,  R,G,RBgSD,GBgSD,m,logb,logSNR,noSNR):
	NData=len(R);
	
	print >> stderr,"using m=",m;
	minSNR=1000000000;
	maxSNR=-1000000000;
	
	logbSNR=log(logSNR);	

	for i in range(0,NData):
		r=R[i];
		g=G[i];
		
		newr=float(r)*m;
		

		if not noSNR:
			rbgsd=RBgSD[i];
			gbgsd=GBgSD[i];
			snr=float(mean(r,g))/max(rbgsd,gbgsd);
		
			if(logSNR>0):
				snr=log(snr)/logbSNR;

			SNR.append(snr);
			maxSNR=max(snr,maxSNR);
			minSNR=min(snr,minSNR);

		
		lognewr=log(newr)/logb;
		logg=log(g)/logb;

		mValue=lognewr-logg;
		aValue=(lognewr+logg)/2

		
		newR.append(newr);
		lognewR.append(lognewr);
		logG.append(logg);
		M.append(mValue);
		A.append(aValue);

	return [minSNR,maxSNR];


def computeULBounds(SNRBins,LL,UL,logLL,logUL,cSNR,minSNR,maxSNR,SNRBinInterval,m,c, logb,SNRLogged):
	csqr=c**2;
	
	
	
	SNRSpan=maxSNR-minSNR;
	numBins=int(ceil(SNRSpan/SNRBinInterval))+1;
	
	
	for binKey in range(0,numBins):
		rawXsnr=minSNR+binKey*SNRBinInterval;

		if(SNRLogged>0):
			snrOfCurrentBin=SNRLogged**(minSNR+binKey*SNRBinInterval);
		else:
			snrOfCurrentBin=minSNR+binKey*SNRBinInterval;

		print >> stderr, "calculating bin", binKey, "of",numBins,"SNR=",snrOfCurrentBin,

		cSNRsqr=csqr+(float(1)/snrOfCurrentBin)**2;
		csnr=sqrt(cSNRsqr);
		


		(c,ll,ul,mean,sd)=polyFitCI95(csnr);
		ll*=m;
		ul*=m;

		UL.append(ul);
		LL.append(ll);

		print >> stderr,"csnr=",csnr,"ll=",ll,"ul=",ul;

		SNRBins.append(rawXsnr);
		
		if(ul<=0):
			logUL.append("nan");
		else:
			logUL.append(log(ul)/logb);
		if(ll<=0):
			logLL.append("nan");
		else:		
			logLL.append(log(ll)/logb);
		
		cSNR.append(csnr);


def getY3UL(x1,y1,x2,y2,x3):
	if(y1=="nan" or y2=="nan"):
		return "nan";

	return float(y1-y2)/(x1-x2)*(x3-x2)+y2;
		


def getY3LL(x1,y1,x2,y2,x3):
	if(y1=="nan" or y2=="nan"):
		return "nan"
	
	return float(y2-y1)/(x2-x1)*(x3-x1)+y1;


def DivideIntoThreeNoSNR(UpGeneID,UpRFlag,UpGFlag,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddlelogR,MiddlelogG,MiddleA,MiddleM,logul,logll,GeneID,RFlag,GFlag,M,A,logR,logG):
	nDataPoints=len(GeneID);

	for i in range(0,nDataPoints):

		geneid=GeneID[i];
		logr=logR[i];
		logg=logG[i];
		mvalue=M[i];
		avalue=A[i];
		rflag=RFlag[i];
		gflag=GFlag[i];
		

		
		if(mvalue>logul):
				UpA.append(avalue);
				UpGeneID.append(geneid);
				UplogR.append(logr);
				UplogG.append(logg);
				UpM.append(mvalue);
				UpRFlag.append(rflag);
				UpGFlag.append(gflag);
		elif(mvalue<logll):
				DownA.append(avalue);
				DownGeneID.append(geneid);
				DownlogR.append(logr);
				DownlogG.append(logg);
				DownM.append(mvalue);	
				DownRFlag.append(rflag);
				DownGFlag.append(gflag);				
		else:
				MiddleA.append(avalue);
				MiddleGeneID.append(geneid);
				MiddlelogR.append(logr);
				MiddlelogG.append(logg);
				MiddleM.append(mvalue);				
				MiddleRFlag.append(rflag);
				MiddleGFlag.append(gflag);				
			


def DivideIntoThree(UpGeneID,UpRFlag,UpGFlag,UpSNR,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownSNR,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddleSNR,MiddlelogR,MiddlelogG,MiddleA,MiddleM,logSNRBins,minSNR,SNRBinInterval,logUL,logLL,GeneID,RFlag,GFlag,SNR,M,A,logR,logG):
	nDataPoints=len(GeneID);
	nBins=len(logSNRBins);	
	for i in range(0,nDataPoints):
		snr=SNR[i];
		lowBinKey=int((snr-minSNR)/SNRBinInterval);
		highBinKey=lowBinKey+1;
		geneid=GeneID[i];
		logr=logR[i];
		logg=logG[i];
		mvalue=M[i];
		avalue=A[i];
		rflag=RFlag[i];
		gflag=GFlag[i];

		if(lowBinKey>=0 and lowBinKey<nBins and highBinKey>=0 and highBinKey<nBins):
			x1=logSNRBins[lowBinKey];
			x2=logSNRBins[highBinKey];
			
			#Up
			ul_y1=logUL[lowBinKey];
			ul_y2=logUL[highBinKey];
			ul_y3=getY3UL(x1,ul_y1,x2,ul_y2,snr);

			#Down 
			ll_y1=logLL[lowBinKey];
			ll_y2=logLL[highBinKey];
			ll_y3=getY3LL(x1,ll_y1,x2,ll_y2,snr);

			if(ul_y3!="nan" and mvalue>ul_y3):
				UpA.append(avalue);
				UpGeneID.append(geneid);
				UpSNR.append(snr);
				UplogR.append(logr);
				UplogG.append(logg);
				UpM.append(mvalue);
				UpRFlag.append(rflag);
				UpGFlag.append(gflag);
			elif(ll_y3!="nan" and mvalue<ll_y3):
				DownA.append(avalue);
				DownGeneID.append(geneid);
				DownSNR.append(snr);
				DownlogR.append(logr);
				DownlogG.append(logg);
				DownM.append(mvalue);	
				DownRFlag.append(rflag);
				DownGFlag.append(gflag);				
			else:
				MiddleA.append(avalue);
				MiddleGeneID.append(geneid);
				MiddleSNR.append(snr);
				MiddlelogR.append(logr);
				MiddlelogG.append(logg);
				MiddleM.append(mvalue);				
				MiddleRFlag.append(rflag);
				MiddleGFlag.append(gflag);			
			
					
			
		else:
			MiddleA.append(avalue);
			MiddleGeneID.append(geneid);
			MiddleSNR.append(snr);
			MiddlelogR.append(logr);
			MiddlelogG.append(logg);
			MiddleM.append(mvalue);
			MiddleRFlag.append(rflag);
			MiddleGFlag.append(gflag);		


def writeOutData(foutData,GeneID,RFlag,logR,GFlag,logG,SNR,A,M,Flag,logData,noSNR):
	L=len(GeneID);
	print >> stderr, Flag, "has",L,"entries to output";

	if noSNR:
		for (geneid,rflag,logr,gflag,logg,a,m) in zip(GeneID,RFlag,logR,GFlag,logG,A,M):
			foutData.write(geneid+"\t"+gflag+"\t"+str(logg)+"\t"+rflag+"\t"+str(logr)+"\t"+"-"+"\t"+str(a)+"\t"+str(m)+"\t"+str(logData**m)+"\t"+Flag+"\n");
	else:
		for (geneid,rflag,logr,gflag,logg,snr,a,m) in zip(GeneID,RFlag,logR,GFlag,logG,SNR,A,M):
			foutData.write(geneid+"\t"+gflag+"\t"+str(logg)+"\t"+rflag+"\t"+str(logr)+"\t"+str(snr)+"\t"+str(a)+"\t"+str(m)+"\t"+str(logData**m)+"\t"+Flag+"\n");
	

def plotRatioStatGeneExpression(filename,RSControlGeneListFilename,geneNamesToPlotFileName,plotName,startRow1,GeneIdCol1,RCol1,RFlagCol1,RBgVarCol1,GCol1,GFlagCol1,GBgVarCol1,iterationLimit,iterationChangeMin,outFilePrefix,formatFigure,SNRBinInterval,useSmartName,logData,logSNR):
	#global ZEROEXP;

	lino=0;
	RCol=RCol1-1;
	GCol=GCol1-1;

	noSNR=False;

	RBgVarCol=RBgVarCol1-1;
	GBgVarCol=GBgVarCol1-1;
	
	if RBgVarCol<0 or GBgVarCol<0:
		noSNR=True;

	GeneIdCol=GeneIdCol1-1;
	RFlagCol=RFlagCol1-1;
	GFlagCol=GFlagCol1-1;
	
		
	logb=log(logData);
	
	
	RValues=[];
	GValues=[];

	MValues=[];
	AValues=[];

	NormRValues=[];

	RBGSD=[];
	GBGSD=[];

	RFlag=[];
	GFlag=[];

	logNormRValues=[];
	logGValues=[];

	GeneIDs=[];
	SNR=[];

	

#load control gene names
	controlGeneList=loadList(RSControlGeneListFilename);

#load gene names to plot
	toPlotGenes=loadList(geneNamesToPlotFileName);

#start reading data from file
	fin=open(filename);

	
		
	if(useSmartName):
		#use the first line
		line=fin.readline();
		line=line.strip();
		spliton=line.split("\t");
		RLabel=spliton[RCol];
		GLabel=spliton[GCol];

		if(plotName==""):
			plotName=RLabel+" vs "+GLabel;

		plotNameLessFancy=RLabel+"-"+GLabel;
		yaxisLabel=RLabel+"/"+GLabel;
		#outFileData+=plotNameLessFancy+".txt"; #use as prefix

		outFileFigureSNRM=outFilePrefix+plotNameLessFancy+".SNRM."+formatFigure;#use as prefix
		outFileFigureRG=outFilePrefix+plotNameLessFancy+".RG."+formatFigure;#use as prefix
		outFileFigureMA=outFilePrefix+plotNameLessFancy+".MA."+formatFigure;#use as prefix
		
		outFileData=outFilePrefix+plotNameLessFancy+".txt"
		#outFileDataHigh+=plotNameLessFancy+".up."+str(thr)+".txt"; #use as prefix
		#outFileDataLow+=plotNameLessFancy+".down."+str(thr)+".txt"; #use as prefix
		#outFileDataCentral+=plotNameLessFancy+".middle."+str(thr)+".txt"; #use as prefix

		fin.close();
		fin=open(filename);
	



	
	for line in fin:
		lino+=1;
			
		line=line.strip();
		spliton=line.split("\t");
	#	spliton=line.split("\t");
		
	#	lineOut="";		
		
	#	for i in range(GeneIdColStart,GeneIdColEnd1):
	#		lineOut+=(spliton[i]+"\t");
	#	lineOut+=(spliton[RCol]+"\t");
	#	lineOut+=(spliton[GCol]+"\t");
		#print >> stderr,"lino=",lino,"startRow=",startRow1;	

		if(lino<startRow1):
			
			continue; #not neccessary?						
		else:
			RValue=float(spliton[RCol]);
			GValue=float(spliton[GCol]);

			logRValue=log(RValue)/logb;
			logGValue=log(GValue)/logb;	

			GeneIDs.append(spliton[GeneIdCol].split(",")[0]);
			RValues.append(RValue);
			GValues.append(GValue);


			if(RFlagCol<0):
				RFlag.append('-');
			else:
				RFlag.append(spliton[RFlagCol]);

			if(GFlagCol<0):
				GFlag.append('-');
			else:			
				GFlag.append(spliton[GFlagCol]);
			

			if not noSNR:	
				RBGSD.append(sqrt(float(spliton[RBgVarCol])));
				GBGSD.append(sqrt(float(spliton[GBgVarCol])));

	fin.close();

#now eliminate outlier controls
#	eliminateOutlierControl(RValues,GValues,indices,2);

#now do Ratio Statistics:
	SNR=[];
	SNRBins=[];
	UL=[];
	LL=[];
	logUL=[];
	logLL=[];
	cSNR=[];

	##logSNR=10;

	(m,c,ll,ul,miu,sd)=iterativeRatioStat(GeneIDs,RValues,GValues,1,controlGeneList,2,iterationLimit,iterationChangeMin);

	
	
	logll=log(ll)/logb;
	logul=log(ul)/logb;

	print >> stderr,"m=",m,"c=",c,"ll=",ll,"logll=",logll,"ul=",ul,"logul=",logul,"miu=",miu,"sd=",sd,
	##if not noSNR:
	(minSNR,maxSNR)=FillUpSNR(SNR,MValues,AValues,NormRValues,logNormRValues,logGValues,  RValues,GValues,RBGSD,GBGSD,m,logb,logSNR,noSNR);
	
	if not noSNR:	
		computeULBounds(SNRBins,LL,UL,logLL,logUL,cSNR,minSNR,maxSNR,SNRBinInterval,m,c, logb,logSNR);

	UpA=[];
	UpGeneID=[];#(geneid);
	UpSNR=[];#(snr);
	UplogR=[];#(logr);
	UplogG=[];#(logg);
	UpM=[];#(mvalue);
	UpBG=[];
	UpRFlag=[];
	UpGFlag=[];

	DownA=[];
	DownGeneID=[];#(geneid);
	DownSNR=[];#(snr);
	DownlogR=[];#(logr);
	DownlogG=[];#(logg);
	DownM=[];#(mvalue);	
	DownRFlag=[];
	DownGFlag=[];				
		
	MiddleA=[];	
	MiddleGeneID=[];#(geneid);
	MiddleSNR=[];#(snr);
	MiddlelogR=[];#(logr);
	MiddlelogG=[];#(logg);
	MiddleM=[];#(mvalue);				
	MiddleRFlag=[];
	MiddleGFlag=[];
	

	if noSNR:
		DivideIntoThreeNoSNR(UpGeneID,UpRFlag,UpGFlag,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddlelogR,MiddlelogG,MiddleA,MiddleM,logul,logll,GeneIDs,RFlag,GFlag,MValues,AValues,logNormRValues,logGValues);
	else:		
		DivideIntoThree(UpGeneID,UpRFlag,UpGFlag,UpSNR,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownSNR,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddleSNR,MiddlelogR,MiddlelogG,MiddleA,MiddleM,SNRBins,minSNR,SNRBinInterval,logUL,logLL,GeneIDs,RFlag,GFlag,SNR,MValues,AValues,logNormRValues,logGValues);




#SNR-M plot
	if not noSNR:
		figure();
		#scatter(SNR,MValues,marker='s',color='black',s=1);
		scatter(UpSNR,UpM,marker='s',color='red',s=1);
		scatter(MiddleSNR,MiddleM,marker='s',color='blue',s=1);
		scatter(DownSNR,DownM,marker='s',color='green',s=1);

		title(plotName);
		xlabel("logSNR");
		ylabel("log("+yaxisLabel+")");
	
		rc('lines', linewidth=2)


		print >> stderr,"m=",m,"c=",c,"log LL=",logll,"log UL=",logul;
		plot(SNRBins,logUL,'-r');
		axhline(color='grey');
		plot(SNRBins,logLL,'-g');
		
		for geneName in toPlotGenes:
			geneNameS=geneName.split("=");
			geneID=geneNameS[0];
		
			lspliton=len(geneNameS);
			geneDisplay="";		
			color='k';		
	
			if(lspliton>1 and len(geneNameS[1])>0):
				geneDisplay=geneNameS[1];
		
			if(lspliton>2 and len(geneNameS[2])>0):
				color=geneNameS[2];
		
			drawGeneByName(GeneIDs,SNR,MValues,geneID,geneDisplay,color);


			#axhline(y=logul,xmin=minSNR,xmax=maxSNR,color='red');
			#axhline(y=logll,xmin=minSNR,xmax=maxSNR,color='green');

		savefig(outFileFigureSNRM,format=formatFigure);

#MA plot
	figure();
	#scatter(SNR,MValues,marker='s',color='black',s=1);
	scatter(UpA,UpM,marker='s',color='red',s=1);
	scatter(MiddleA,MiddleM,marker='s',color='blue',s=1);
	scatter(DownA,DownM,marker='s',color='green',s=1);

	if noSNR:
		axhline(y=logul,color='red');
		axhline(y=logll,color='green');

	for geneName in toPlotGenes:
		geneNameS=geneName.split("=");
		geneID=geneNameS[0];
		
		lspliton=len(geneNameS);
		geneDisplay="";		
		color='k';		
	
		if(lspliton>1 and len(geneNameS[1])>0):
			geneDisplay=geneNameS[1];
		
		if(lspliton>2 and len(geneNameS[2])>0):
			color=geneNameS[2];
		
		
		drawGeneByName(GeneIDs,AValues,MValues,geneID,geneDisplay,color);

	title(plotName);
	xlabel("A=mean log of "+RLabel+"and"+GLabel);
	ylabel("M=log("+yaxisLabel+")");

	savefig(outFileFigureMA,format=formatFigure);

#RG plot
	figure();
	#scatter(SNR,MValues,marker='s',color='black',s=1);
	scatter(UplogG,UplogR,marker='s',color='red',s=1);
	scatter(MiddlelogG,MiddlelogR,marker='s',color='blue',s=1);
	scatter(DownlogG,DownlogR,marker='s',color='green',s=1);

	title(plotName);
	xlabel("log"+GLabel);
	ylabel("log"+RLabel);

	for geneName in toPlotGenes:
		geneNameS=geneName.split("=");
		geneID=geneNameS[0];
		
		lspliton=len(geneNameS);
		geneDisplay="";		
		color='k';		
	
		if(lspliton>1 and len(geneNameS[1])>0):
			geneDisplay=geneNameS[1];
		
		if(lspliton>2 and len(geneNameS[2])>0):
			color=geneNameS[2];
		
		
		drawGeneByName(GeneIDs,logGValues,logNormRValues,geneID,geneDisplay,color);
	
	xlim(xmin=min(logGValues))
	ylim(ymin=min(logNormRValues))

	savefig(outFileFigureRG,format=formatFigure);

#OutputFiles
	foutData=open(outFileData,"w");
	
	foutData.write("GeneID\t"+GLabel+".Flag\tlog"+GLabel+"\t"+RLabel+".Flag\tlog"+RLabel+"\tlogSNR\tA(avglog)\tM(logRatio)\tRatio\tFlag\n");
	
	
	writeOutData(foutData,UpGeneID,UpRFlag,UplogR,UpGFlag,UplogG,UpSNR,UpA,UpM,"Up",logData,noSNR);	
	writeOutData(foutData,DownGeneID,DownRFlag,DownlogR,DownGFlag,DownlogG,DownSNR,DownA,DownM,"Down",logData,noSNR);
	writeOutData(foutData,MiddleGeneID,MiddleRFlag,MiddlelogR,MiddleGFlag,MiddlelogG,MiddleSNR,MiddleA,MiddleM,"Middle",logData,noSNR);
	
	foutData.close();


#opts,argv=getopt(argv[1:],'',['Cols1ToCopy=']);

if(len(argv)<21 ):
	print >> sys.stderr,"Usage: "+argv[0]+" filename,RSControlGeneListFilename,GenesToPlotFilename,plotName,startRow1,GeneIdCol1,RCol1,RFlagCol1>0|[0='-'],RBgVarCol1>0|[0=ignored],GCol1,GFlagCol1>0[0='-'],GBgVarCol1>0[0=ignored],iterationLimit,iterationChangeMin,outFilesPrefix,formatFigure,SNRBinInterval,useSmartName,logData,logSNR";
	exit();




plotRatioStatGeneExpression(argv[1],argv[2],argv[3],argv[4],int(argv[5]),int(argv[6]),int(argv[7]),int(argv[8]),int(argv[9]),int(argv[10]),int(argv[11]),int(argv[12]),int(argv[13]),float(argv[14]),argv[15],argv[16],float(argv[17]),(argv[18].lower()=='y'),float(argv[19]),float(argv[20]));


