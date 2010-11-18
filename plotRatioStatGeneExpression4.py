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
from math import ceil,fabs;

from pvalue_module import *

from AudicClaverieStatInterface import *

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
			

def DivideIntoThreeAC(NEGeneIDAC,NERFlagAC,NEGFlagAC,NElogRAC,NElogGAC,NEPvalueAC,NEFDRAC,NERReadsAC,NEGReadsAC,UpGeneIDAC,UpRFlagAC,UpGFlagAC,UplogRAC,UplogGAC,UpPvalueAC,UpFDRAC,UpRReadsAC,UpGReadsAC,Up2GeneIDAC,Up2RFlagAC,Up2GFlagAC,Up2logRAC,Up2logGAC,Up2PvalueAC,Up2FDRAC,Up2RReadsAC,Up2GReadsAC,DownGeneIDAC,DownRFlagAC,DownGFlagAC,DownlogRAC,DownlogGAC,DownPvalueAC,DownFDRAC,DownRReadsAC,DownGReadsAC,Down2GeneIDAC,Down2RFlagAC,Down2GFlagAC,Down2logRAC,Down2logGAC,Down2PvalueAC,Down2FDRAC,Down2RReadsAC,Down2GReadsAC,MiddleGeneIDAC,MiddleRFlagAC,MiddleGFlagAC,MiddlelogRAC,MiddlelogGAC,MiddlePvalueAC,MiddleFDRAC,MiddleRReadsAC,MiddleGReadsAC,GeneIDs,RFlag,GFlag,logNormRValues,logGValues,ACPvalue,ACFDR,RReads,GReads,FDRCutOff,foldCutOff,logb):
	
	logfoldCutOff=log(foldCutOff)/logb
	for gid,rflag,gflag,lognormrvalue,loggvalue,acpval,acfdr,rval,gval in zip(GeneIDs,RFlag,GFlag,logNormRValues,logGValues,ACPvalue,ACFDR,RReads,GReads):
		if int(rflag)<1 and int(gflag)<1:
					NEGeneIDAC.append(gid)
					NERFlagAC.append(rflag)
					NEGFlagAC.append(gflag)
					NElogRAC.append(lognormrvalue)
					NElogGAC.append(loggvalue)
					NEPvalueAC.append(acpval)
					NEFDRAC.append(acfdr)
					NERReadsAC.append(rval)
					NEGReadsAC.append(gval)
					continue
			
		if acfdr<FDRCutOff:
			#differential!
			if rval>=gval:
				#r value is bigger!
				#so it's up
				if fabs(lognormrvalue-loggvalue)>=logfoldCutOff:  #fold and stat pass
					Up2GeneIDAC.append(gid)
					Up2RFlagAC.append(rflag)
					Up2GFlagAC.append(gflag)
					Up2logRAC.append(lognormrvalue)
					Up2logGAC.append(loggvalue)
					Up2PvalueAC.append(acpval)
					Up2FDRAC.append(acfdr)
					Up2RReadsAC.append(rval)
					Up2GReadsAC.append(gval)				
				else:
					UpGeneIDAC.append(gid)
					UpRFlagAC.append(rflag)
					UpGFlagAC.append(gflag)
					UplogRAC.append(lognormrvalue)
					UplogGAC.append(loggvalue)
					UpPvalueAC.append(acpval)
					UpFDRAC.append(acfdr)
					UpRReadsAC.append(rval)
					UpGReadsAC.append(gval)
			else:
				if fabs(lognormrvalue-loggvalue)>=logfoldCutOff:  #fold and stat pass
					Down2GeneIDAC.append(gid)
					Down2RFlagAC.append(rflag)
					Down2GFlagAC.append(gflag)
					Down2logRAC.append(lognormrvalue)
					Down2logGAC.append(loggvalue)
					Down2PvalueAC.append(acpval)
					Down2FDRAC.append(acfdr)	
					Down2RReadsAC.append(rval)
					Down2GReadsAC.append(gval)	

				else:
					DownGeneIDAC.append(gid)
					DownRFlagAC.append(rflag)
					DownGFlagAC.append(gflag)
					DownlogRAC.append(lognormrvalue)
					DownlogGAC.append(loggvalue)
					DownPvalueAC.append(acpval)
					DownFDRAC.append(acfdr)	
					DownRReadsAC.append(rval)
					DownGReadsAC.append(gval)			
		else:
			MiddleGeneIDAC.append(gid)
			MiddleRFlagAC.append(rflag)
			MiddleGFlagAC.append(gflag)
			MiddlelogRAC.append(lognormrvalue)
			MiddlelogGAC.append(loggvalue)
			MiddlePvalueAC.append(acpval)
			MiddleFDRAC.append(acfdr)	
			MiddleRReadsAC.append(rval)
			MiddleGReadsAC.append(gval)	

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

def writeOutDataAC(foutData,UpGeneIDAC,UpRFlagAC,UplogRAC,UpGFlagAC,UplogGAC,Flag,logData,UpPvalueAC,UpFDRAC,RReads,GReads,totalRReads,totalGReads):
	for (geneid,rflag,logr,gflag,logg,pval,fdr,rread,gread) in zip(UpGeneIDAC,UpRFlagAC,UplogRAC,UpGFlagAC,UplogGAC,UpPvalueAC,UpFDRAC,RReads,GReads):
		a=(logg+logr)/2
		m=logr-logg
		
		#foutData.write("GeneID\t"+GLabel+".Flag\tlog"+GLabel+"\t"+RLabel+".Flag\tlog"+RLabel+"\tA(avglog)\tM(logRatio)\tRatio\tFlag\tAudicClaveriePvalue\tAudicClaverieFDR\n");
		foutData.write(geneid+"\t"+gflag+"\t"+str(logg)+"\t"+rflag+"\t"+str(logr)+"\t"+str(a)+"\t"+str(m)+"\t"+str(logData**m)+"\t"+Flag+"\t"+str(pval)+"\t"+str(fdr)+"\t"+str(gread)+"\t"+str(rread)+"\t"+str(totalGReads)+"\t"+str(totalRReads)+"\n");

def plotRatioStatGeneExpression(filename,RSControlGeneListFilename,geneNamesToPlotFileName,plotName,startRow1,GeneIdCol1,RCol1,RFlagCol1,RBgVarCol1,GCol1,GFlagCol1,GBgVarCol1,iterationLimit,iterationChangeMin,outFilePrefix,formatFigure,SNRBinInterval,useSmartName,logData,logSNR,RReadCol1,GReadCol1,totalRReads,totalGReads,FDRCutOff,foldCutOff,sizeDot,showNumber,alpha,beta,minValueAdd):
	#global ZEROEXP;

	lino=0;
	RCol=RCol1-1;
	GCol=GCol1-1;
	RReadCol=RReadCol1-1
	GReadCol=GReadCol1-1

	noSNR=False;

	RBgVarCol=RBgVarCol1-1;
	GBgVarCol=GBgVarCol1-1;
	
	if RBgVarCol<0 or GBgVarCol<0:
		noSNR=True;

	GeneIdCol=GeneIdCol1-1;
	RFlagCol=RFlagCol1-1;
	GFlagCol=GFlagCol1-1;
	
		
	logb=log(logData);
	
	RReads=[]
	GReads=[]

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
		outFileFigureRGAC=outFilePrefix+plotNameLessFancy+".RGAC."+formatFigure;
		outFileData=outFilePrefix+plotNameLessFancy+".txt"
		outFileDataAC=outFilePrefix+plotNameLessFancy+".AC.txt"
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

			if RReadCol>=0 and GReadCol>=0:
				RRead=int(spliton[RReadCol])
				GRead=int(spliton[GReadCol])

				RReads.append(RRead)
				GReads.append(GRead)

				#print >> stderr, spliton[GeneIdCol].split(",")[0],"RReads=",RRead,"GReads",GRead

				

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
	
	ACpvalue=[]
	ACFDR=[]
	

	nnnn=0
	NNNN=len(RReads)
	if totalRReads >0 and totalGReads>0: #calculate AudicClaverie statistics
		
		XYN1N2=[]
		for r,g in zip(RReads,GReads):
			nnnn+=1
			
			if r>=g: #the bigger one is the y
				y=r
				x=g
				n2=totalRReads
				n1=totalGReads
			else:
				y=g
				x=r
				n2=totalGReads
				n1=totalRReads

			XYN1N2.append([x,y,n1,n2])
			
		
			if nnnn%1000==0:
				print >> stderr,"calculate Audic Claverie",nnnn,"of",NNNN
				if len(XYN1N2)>0:
					AudicClaverieStatInPlace(XYN1N2)

					for x,y,n1,n2,dummy,pvalue in XYN1N2:
						ACpvalue.append(pvalue)

				XYN1N2=[]

		if len(XYN1N2)>0:
			AudicClaverieStatInPlace(XYN1N2)
			for x,y,n1,n2,dummy,pvalue in XYN1N2:
				ACpvalue.append(pvalue)

		ACFDR=getFDRfromPvalue(ACpvalue)
		
		
		
		
	
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
	

	UpGeneIDAC=[]
	UpRFlagAC=[]
	UpGFlagAC=[]
	UplogRAC=[]
	UplogGAC=[]
	Up2GeneIDAC=[]
	Up2RFlagAC=[]
	Up2GFlagAC=[]
	Up2logRAC=[]
	Up2logGAC=[]
	DownGeneIDAC=[]
	DownRFlagAC=[]
	DownGFlagAC=[]
	DownlogRAC=[]
	DownlogGAC=[]
	Down2GeneIDAC=[]
	Down2RFlagAC=[]
	Down2GFlagAC=[]
	Down2logRAC=[]
	Down2logGAC=[]
	MiddleGeneIDAC=[]
	MiddleRFlagAC=[]
	MiddleGFlagAC=[]
	MiddlelogRAC=[]
	MiddlelogGAC=[]
	UpPvalueAC=[]
	MiddlePvalueAC=[]
	DownPvalueAC=[]
	Up2PvalueAC=[]
	Down2PvalueAC=[]
	UpFDRAC=[]
	MiddleFDRAC=[]
	DownFDRAC=[]
	Up2FDRAC=[]
	Down2FDRAC=[]
	UpRReadsAC=[]
	UpGReadsAC=[]
	DownRReadsAC=[]
	DownGReadsAC=[]
	Up2RReadsAC=[]
	Up2GReadsAC=[]
	Down2RReadsAC=[]
	Down2GReadsAC=[]
	MiddleRReadsAC=[]
	MiddleGReadsAC=[]

	NEGeneIDAC=[]
	NERFlagAC=[]
	NEGFlagAC=[]
	NElogRAC=[]
	NElogGAC=[]
	NEPvalueAC=[]
	NEFDRAC=[]
	NERReadsAC=[]
	NEGReadsAC=[]




	if noSNR:
		DivideIntoThreeNoSNR(UpGeneID,UpRFlag,UpGFlag,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddlelogR,MiddlelogG,MiddleA,MiddleM,logul,logll,GeneIDs,RFlag,GFlag,MValues,AValues,logNormRValues,logGValues);
	else:		
		DivideIntoThree(UpGeneID,UpRFlag,UpGFlag,UpSNR,UplogR,UplogG,UpA,UpM,DownGeneID,DownRFlag,DownGFlag,DownSNR,DownlogR,DownlogG,DownA,DownM,MiddleGeneID,MiddleRFlag,MiddleGFlag,MiddleSNR,MiddlelogR,MiddlelogG,MiddleA,MiddleM,SNRBins,minSNR,SNRBinInterval,logUL,logLL,GeneIDs,RFlag,GFlag,SNR,MValues,AValues,logNormRValues,logGValues);

	if len(ACFDR)>0: #,ACFDR,RValues,GValues,FDRCutOff):
		DivideIntoThreeAC(NEGeneIDAC,NERFlagAC,NEGFlagAC,NElogRAC,NElogGAC,NEPvalueAC,NEFDRAC,NERReadsAC,NEGReadsAC,UpGeneIDAC,UpRFlagAC,UpGFlagAC,UplogRAC,UplogGAC,UpPvalueAC,UpFDRAC,UpRReadsAC,UpGReadsAC,Up2GeneIDAC,Up2RFlagAC,Up2GFlagAC,Up2logRAC,Up2logGAC,Up2PvalueAC,Up2FDRAC,Up2RReadsAC,Up2GReadsAC,DownGeneIDAC,DownRFlagAC,DownGFlagAC,DownlogRAC,DownlogGAC,DownPvalueAC,DownFDRAC,DownRReadsAC,DownGReadsAC,Down2GeneIDAC,Down2RFlagAC,Down2GFlagAC,Down2logRAC,Down2logGAC,Down2PvalueAC,Down2FDRAC,Down2RReadsAC,Down2GReadsAC,MiddleGeneIDAC,MiddleRFlagAC,MiddleGFlagAC,MiddlelogRAC,MiddlelogGAC,MiddlePvalueAC,MiddleFDRAC,MiddleRReadsAC,MiddleGReadsAC,GeneIDs,RFlag,GFlag,logNormRValues,logGValues,ACpvalue,ACFDR,RReads,GReads,FDRCutOff,foldCutOff,logb)



#SNR-M plot
	if not noSNR:
		figure(figsize=(8, 8));
		#scatter(SNR,MValues,marker='o',color='black',s=sizeDot);
		if len(UpSNR)>0:
			scatter(UpSNR,UpM,marker='o',color='red',s=sizeDot);
		if len(MiddleSNR)>0:
			scatter(MiddleSNR,MiddleM,marker='o',color='blue',s=sizeDot);
		
		if len(DownSNR)>0:
			scatter(DownSNR,DownM,marker='o',color='green',s=sizeDot);

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
	figure(figsize=(8, 8));
	#scatter(SNR,MValues,marker='o',color='black',s=sizeDot);
	if len(UpA)>0:
		scatter(UpA,UpM,marker='o',color='red',s=sizeDot);
	if len(MiddleA)>0:
		scatter(MiddleA,MiddleM,marker='o',color='blue',s=sizeDot);
	
	if len(DownA)>0:
		scatter(DownA,DownM,marker='o',color='green',s=sizeDot);

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
	figure(figsize=(8, 8));
	#scatter(SNR,MValues,marker='o',color='black',s=sizeDot);
	if len(UplogG)>0:
		scatter(UplogG,UplogR,marker='o',color='red',s=sizeDot);
	if len(MiddlelogG)>0:
		scatter(MiddlelogG,MiddlelogR,marker='o',color='blue',s=sizeDot);
	if len(DownlogG)>0:
		scatter(DownlogG,DownlogR,marker='o',color='green',s=sizeDot);

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


	middlecolor=[0.0,0.0,1.0]
	up2color=[1.0,0.0,0.0]
	down2color=[0.0,1.0,0.0]
	necolor="grey"

	for x in [alpha]:
		for y in [beta]:
#RG plot with Audic Claverie
			print >> stderr,"working on AC x=",x,"y=",y
			X=1-x
			Y=1-y
			mr,mg,mb=middlecolor
			ur,ug,ub=up2color
			dr,dg,db=down2color
			upcolor=[mr*x+ur*X,mg*x+ug*X,mb*x+ub*X]
			downcolor=[mr*y+dr*Y,mg*y+dg*Y,mb*y+db*Y]
			
			figure(figsize=(8, 8));
			#scatter(SNR,MValues,marker='o',color='black',s=sizeDot);
			

			
			if len(MiddlelogGAC)>0:
				scatter(MiddlelogGAC,MiddlelogRAC,marker='o',color=middlecolor,s=sizeDot);

			if len(NElogGAC)>0:
				scatter(NElogGAC,NElogRAC,marker='o',color=necolor,s=sizeDot);

			if len(UplogGAC)>0:
				scatter(UplogGAC,UplogRAC,marker='o',color=upcolor,s=sizeDot);

	

			if len(DownlogGAC)>0:
				scatter(DownlogGAC,DownlogRAC,marker='o',color=downcolor,s=sizeDot);


			if len(Up2logGAC)>0:
				scatter(Up2logGAC,Up2logRAC,marker='o',color=up2color,s=sizeDot);


			if len(Down2logGAC)>0:
				scatter(Down2logGAC,Down2logRAC,marker='o',color=down2color,s=sizeDot);

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
	
	
			#if showNumber:
			#	lUplogGAC=len(UplogGAC)
			#	lMiddlelogGAC=len(MiddlelogGAC)
			#	lDownlogGAC=len(DownlogGAC)

			#	text(min(logGValues),max(logNormRValues),str(lUplogGAC),color='red',horizontalalignment='left',verticalalignment='top')
			#	text(max(logGValues),max(logNormRValues),str(lMiddlelogGAC),color='black',horizontalalignment='right',verticalalignment='top')
			#	text(max(logGValues),min(logNormRValues),str(lDownlogGAC),color='green',horizontalalignment='right',verticalalignment='bottom')

			xlim(xmin=min(logGValues)-minValueAdd,xmax=max(logGValues)*1.1)
			ylim(ymin=min(logNormRValues)-minValueAdd,ymax=max(logNormRValues)*1.1)

			savefig(outFileFigureRGAC,format=formatFigure);
			#savefig(outFileFigureRGAC+"_"+str(x)+"_"+str(y)+".png",format=formatFigure);

#OutputFiles
	foutData=open(outFileData,"w");
	
	foutData.write("GeneID\t"+GLabel+".Flag\tlog"+GLabel+"\t"+RLabel+".Flag\tlog"+RLabel+"\tlogSNR\tA(avglog)\tM(logRatio)\tRatio\tFlag\n");
	
	
	writeOutData(foutData,UpGeneID,UpRFlag,UplogR,UpGFlag,UplogG,UpSNR,UpA,UpM,"Up",logData,noSNR);	
	writeOutData(foutData,DownGeneID,DownRFlag,DownlogR,DownGFlag,DownlogG,DownSNR,DownA,DownM,"Down",logData,noSNR);
	writeOutData(foutData,MiddleGeneID,MiddleRFlag,MiddlelogR,MiddleGFlag,MiddlelogG,MiddleSNR,MiddleA,MiddleM,"Middle",logData,noSNR);
	
	foutData.close();


	foutData=open(outFileDataAC,"w");
	
	foutData.write("GeneID\t"+GLabel+".Flag\tlog"+GLabel+"\t"+RLabel+".Flag\tlog"+RLabel+"\tA(avglog)\tM(logRatio)\tRatio\tFlag\tAudicClaveriePvalue\tAudicClaverieFDR\t"+GLabel+".Reads\t"+RLabel+".Reads\t"+GLabel+".totalReads\t"+RLabel+".totalReads\n");
	
	writeOutDataAC(foutData,Up2GeneIDAC,Up2RFlagAC,Up2logRAC,Up2GFlagAC,Up2logGAC,"Up2",logData,Up2PvalueAC,Up2FDRAC,Up2RReadsAC,Up2GReadsAC,totalRReads,totalGReads);		
	writeOutDataAC(foutData,UpGeneIDAC,UpRFlagAC,UplogRAC,UpGFlagAC,UplogGAC,"Up",logData,UpPvalueAC,UpFDRAC,UpRReadsAC,UpGReadsAC,totalRReads,totalGReads);	
	writeOutDataAC(foutData,Down2GeneIDAC,Down2RFlagAC,Down2logRAC,Down2GFlagAC,Down2logGAC,"Down2",logData,Down2PvalueAC,Down2FDRAC,Down2RReadsAC,Down2GReadsAC,totalRReads,totalGReads);
	writeOutDataAC(foutData,DownGeneIDAC,DownRFlagAC,DownlogRAC,DownGFlagAC,DownlogGAC,"Down",logData,DownPvalueAC,DownFDRAC,DownRReadsAC,DownGReadsAC,totalRReads,totalGReads);
	writeOutDataAC(foutData,MiddleGeneIDAC,MiddleRFlagAC,MiddlelogRAC,MiddleGFlagAC,MiddlelogGAC,"Middle",logData,MiddlePvalueAC,MiddleFDRAC,MiddleRReadsAC,MiddleGReadsAC,totalRReads,totalGReads);
	writeOutDataAC(foutData,NEGeneIDAC,NERFlagAC,NElogRAC,NEGFlagAC,NElogGAC,"NotExpressed",logData,NEPvalueAC,NEFDRAC,NERReadsAC,NEGReadsAC,totalRReads,totalGReads);
	
	foutData.close();



#opts,argv=getopt(argv[1:],'',['Cols1ToCopy=']);

if(len(argv)<27 ):
	print >> sys.stderr,"Usage: "+argv[0]+" filename,RSControlGeneListFilename,GenesToPlotFilename,plotName,startRow1,GeneIdCol1,RCol1,RFlagCol1>0|[0='-'],RBgVarCol1>0|[0=ignored],GCol1,GFlagCol1>0[0='-'],GBgVarCol1>0[0=ignored],iterationLimit,iterationChangeMin,outFilesPrefix,formatFigure,SNRBinInterval,useSmartName,logData,logSNR,RReadCol1[0=:no cal audicClaverie],GReadCol1[0=:no cal audicClaverie],totalRReads[=0:no calculate AudicClaverie],totalGReads[=0:no calculate AudicClaverie],AudicClaverieFDRcutoff[=2:no cutoff],AudicClaveriefoldCutOff[=1:no cutoff]";
	exit();


alpha=0.5
beta=0.5
minValueAdd=0.02
showNumber=False

plotRatioStatGeneExpression(argv[1],argv[2],argv[3],argv[4],int(argv[5]),int(argv[6]),int(argv[7]),int(argv[8]),int(argv[9]),int(argv[10]),int(argv[11]),int(argv[12]),int(argv[13]),float(argv[14]),argv[15],argv[16],float(argv[17]),(argv[18].lower()=='y'),float(argv[19]),float(argv[20]),int(argv[21]),int(argv[22]),int(argv[23]),int(argv[24]),float(argv[25]),float(argv[26]),2,showNumber,alpha,beta,minValueAdd);


