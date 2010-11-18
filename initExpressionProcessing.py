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

import re
from sys import stderr,stdout,argv
from math import log,sqrt
from getopt import getopt,GetoptError
import sys
from albertcommon import *

	
def readInKeyValueFile(filename):
	
	D=dict()
	fin=None
	try:
		fin=open(filename)
		for lin in fin:
			lin=lin.rstrip()
			#print >> stderr, lin
			splitons=lin.split("\t")
			D[splitons[0]]=splitons[1]
	except:
		
		return D
	#finally:
	#	if not fin is None:
	#		fin.close()
	
	return D

def getRegexes(D):
	Regexes=[]
	for K,V in D.items():
		p=re.compile(K)
		Regexes.append([p,V])
	
	return Regexes
	
def replaceField(Regexes,field):
	for patternvalue in Regexes:
		pattern,value=patternvalue
		#print >> stderr, "value=",value
		m=pattern.search(field)
		if m==None:
			continue
		return value
	
	return field


def printLine(printStat,includes,stats,fields,Nfields,col0Values,isHeader,OFS,normHeaderPrefix):
	iInclude=0	
	fieldsToPrint=[]
	if isHeader:
		for printInstruction in printStat:
			#print >> stderr, printInstruction
			if printInstruction=="nvalues":
				for col0 in col0Values:
					fieldsToPrint.append(normHeaderPrefix+Nfields[col0])
			elif printInstruction=="includes":
				for col0 in includes[iInclude]:
					fieldsToPrint.append(fields[col0])
				iInclude+=1
			else:
				fieldsToPrint.append(printInstruction)

	else:
		for printInstruction in printStat:
			if printInstruction=="nvalues":
				for col0 in col0Values:
					fieldsToPrint.append(normHeaderPrefix+Nfields[col0])
			elif printInstruction=="includes":
				for col0 in includes[iInclude]:
					fieldsToPrint.append(fields[col0])
				iInclude+=1
			else:
				fieldsToPrint.append(str(stats[printInstruction]))		

	print >> stdout, OFS.join(fieldsToPrint)

def initExpressionProcessing_Main(filenameIn,normalizerFile,includes,printStat,col0Values,normOp,col0Norm,logBase,filenameRemap,FS,OFS,normHeaderPrefix):
	DRemap=readInKeyValueFile(filenameRemap)
	
	#print >> stderr, DRemap
	#return
	ReMapRegexes=getRegexes(DRemap)
	
	logb=0
	
	if logBase!=0:
		logb=log(logBase)
	
	
	NValues=len(col0Values)
	

	twoFiles=False
	
	fin=generic_istream(filenameIn)
	
	if filenameIn!=normalizerFile:	
		fnorm=generic_istream(normalizerFile)	
		twoFiles=True
	
	lnormCol0=len(col0Norm)

	if lnormCol0==1:
		for i in range(lnormCol0,NValues):
			col0Norm.append(col0Norm[0])
	elif lnormCol0==0:
		for i in range(lnormCol0,NValues):
			col0Norm.append(1)
	
	lino=0
	for line in fin:
		line=line.rstrip()
		fields=line.split(FS)
		
		if twoFiles:
			lineNorm=fnorm.readline().rstrip()
			fieldsNorm=lineNorm.split(FS)
		else:
			fieldsNorm=fields[:] #do a copy instead
			
		lino+=1
		#print >> stderr,"processing line",lino

		printFields=[]	
	
		stats=dict()	
	
		if lino==1:
			if len(DRemap.keys())>0:
				for col0 in col0Values:
					prevField=fields[col0]
					fields[col0]=replaceField(ReMapRegexes,fields[col0])

				for ninc in includes:
					for col0 in ninc:
						prevField=fields[col0]
						fields[col0]=replaceField(ReMapRegexes,fields[col0])						
					#print >> stderr,"replaceField@",(col0+1),"from",prevField,"to",fields[col0]
						
			
			printLine(printStat,includes,stats,fields,fields,col0Values,True,OFS,normHeaderPrefix)
		else:
			sumXsq=0.0
			sumX=0.0
			maxX=-100000000.0
			minX=1000000000.00			
			sumNsq=0.0
			sumN=0.0
			maxN=-100000000.0
			minN=1000000000.00	

			
			Nfields=fields[:]
			
			for col0,col0n in zip(col0Values,col0Norm):
				try:
					fieldValue=float(fields[col0])
				except ValueError: #need a better solution!!
					continue


				sumXsq+=fieldValue**2
				sumX+=fieldValue
				
				if(fieldValue>maxX):
					maxX=fieldValue

				if(fieldValue<minX):
					minX=fieldValue				
				
				if normOp=="-":
					fieldValue-=float(fieldsNorm[col0n])
				elif normOp=="/":
					fieldValue/=float(fieldsNorm[col0n])
				

				if logb!=0:
					#print >> stderr, fieldValue
					#print >> stderr, "logf=",log(fieldValue)
					if fieldValue==0:
						fieldValue=0.00000000001
					fieldValue=log(fieldValue)/logb
				
				Nfields[col0]=str(fieldValue)
				
				sumNsq+=fieldValue**2
				sumN+=fieldValue

				if(fieldValue>maxN):
					maxN=fieldValue	

				if fieldValue<minN:
					minN=fieldValue
			
			mean_X=float(sumX)/NValues
			mean_Xsq=float(sumXsq)/NValues
			var_X=mean_Xsq-(mean_X)**2
			stddev_X=sqrt(var_X*NValues/(NValues-1))

			mean_N=float(sumN)/NValues
			mean_Nsq=float(sumNsq)/NValues
			var_N=mean_Nsq-(mean_N)**2
			stddev_N=sqrt(var_N*NValues/(NValues-1))

		
			CV=stddev_X/mean_X


			stats={ "vmean": mean_X, 
				"vmax": maxX,
				"vmin": minX,
				"vsum": sumX,
				"vstddev": stddev_X,
				"nmean": mean_N,
				"nmin": minN,
				"nmax": maxN,
				"nsum": sumN,
				"nstddev": stddev_N, 
				"vCV": CV }

			printLine(printStat,includes,stats,fields,Nfields,col0Values,False,OFS,normHeaderPrefix)
		

	if twoFiles:
		fnorm.close()

	fin.close()



def usage():
	print >> stderr,programName,"[options...] filenameIn[-:stdin] valuesCol1[a-b,c,...] [-/]normCol1[0:noNormCol;a-b,c,...] logBase[0:no transf]"
	print >> stderr,"Options"
	print >> stderr,"--remap filename\tFiles containing remaps of header fields"
	print >> stderr,"--norm-header-prefix string\tPrefix to add for normalized columns"
	print >> stderr,"--includes [a-b,c,...]\tcols to include and print directly"
	print >> stderr,"--nstddev\tappend stddev of normalized values"
	print >> stderr,"--nmean\tappend mean of normalized values"
	print >> stderr,"--vstddev\tappend stddev of values"
	print >> stderr,"--vmean\tappend mean of values"
	print >> stderr,"--vmin\tappend min value"
	print >> stderr,"--vmax\tappend max value"
	print >> stderr,"--nmin\tappend min normalized value"
	print >> stderr,"--nmax\tappend max normalized value"
	print >> stderr,"--nvalues\t print normalized values"
	print >> stderr,"--normalizer-file filename\tto specify the normalizer file (if not the same as file of values. - means stdin"
	print >> stderr,"the appended values appear as given in the command line"
	explainColumns(stderr)
	sys.exit()

if __name__=="__main__":
	programName=argv[0]

	if len(argv)<5:
		usage()
	else:
		includes=[] #nested list
		printStat=[]
		normalizerFile=""
		normHeaderPrefix=""
		filenameRemap=""
		
		
		startRow=2
		
		headerRow=startRow-1
		if headerRow<1:
			headerRow=1
			
		

		try:
			
			optlist,args=getopt(argv[1:],'',["nstddev","nmean","includes=","nstddev","nvalues","nmean","vstddev","vmean","vmax","nmax","normalizer-file=","norm-header-prefix=","remap=","vmin","nmin","vCV"])
			#print optlist
			
			try:
				filenameIn,valuesCol1ListString,normCol1ListString,logBase=args
			except ValueError:
				usage()
				
			header,prestarts=getHeader(filenameIn,headerRow,startRow,"\t")
			
			for op,val in optlist:
				#print >> stderr,op,val
				if op=="--includes":
					includes.append(getCol0ListFromCol1ListStringAdv(header,val))
					printStat.append(op[2:])
				elif op in ("--nstddev","--nmean","--vmean","--vstddev","--vCV","--vmean","--vmax","--nmax","--nvalues","--vmin","--nmin"):
					printStat.append(op[2:])
				elif op=="--normalizer-file":
					normalizerFile=val
				elif op=="--norm-header-prefix":
					normHeaderPrefix=val
				elif op=="--remap":
					filenameRemap=val
				
			#exit()
			
		except GetoptError, err:
			print >> stderr, err
			usage()
		
		

		
		
		if normalizerFile=="":
			normalizerFile=filenameIn

		col0Norms=[]		
		
				
		normOp=normCol1ListString[0]
		if normOp not in ["0"]:
			#col0Norms=getCol0ListFromCol1ListString(normCol1ListString[1:])
			col0Norms=getCol0ListFromCol1ListStringAdv(header,normCol1ListString[1:])
			print >> sys.stderr,"normOp",normOp,"withcols",col0Norms
		
			

		#col0Values=getCol0ListFromCol1ListString(valuesCol1ListString)
		col0Values=getCol0ListFromCol1ListStringAdv(header,valuesCol1ListString)
			
		initExpressionProcessing_Main(filenameIn,normalizerFile,includes,printStat,col0Values,normOp,col0Norms,float(logBase),filenameRemap,"\t","\t",normHeaderPrefix)


			
