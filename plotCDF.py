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

from pylab import *
from sys import *
from albertcommon import *

from getopt import getopt

def usageExit(programName):
	print >> stderr, "Usage:",programName,"filename colSelector"
	print >> stderr, "Options:"
	print >> stderr, "-F,-t,-d,--fs string input separator string"
	print >> stderr, "-r,--headerRow row set the header row"
	print >> stderr, "--numBins x   set num of bins when draing cdf"
	print >> stderr, "--show-pdf"
	print >> stderr, "--out-img filename"
	print >> stderr, "--min minvalue to bin"
	print >> stderr, "--max maxvalue to bin"
	print >> stderr, "--ylim low,hi"
	explainColumns(stderr)	
	exit()

if __name__=="__main__":
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:s:o:',['ofs=','fs=','headerRow=','numBins=','show-pdf','out-img=','max=','min=','ylim='])

	sort=False
	headerRow=1
	ofs=" "
	fs="\t"
	numBins=100
	outputFile=""
	showPDF=False
	minValue=1000000000000.00
	maxValue=-minValue
	minFixed=False
	maxFixed=False
	YRangeFixed=False
	YRange=False
		
	try:
		fileName,colString=args
	except:
		usageExit(programName)

	for a,v in optlist:
		if a in ["-F","-t","-d","--fs"]:
			fs=replaceSpecialChar(v)			
		elif a in ["-r","--headerRow"]:
			headerRow=int(v)
		elif a in ["--numBins"]:
			numBins=int(v)
		elif a in ['--show-pdf']:
			showPDF=True
		elif a in ['--out-img']:
			outputFile=v
		elif a in ['--min']:
			minValue=float(v)
			minFixed=True
		elif a in ['--max']:
			maxValue=float(v)
			maxFixed=True
		elif a in ['--ylim']:
			YRangeFixed=True
			v=v.split(",")
			YRange=(float(v[0]),float(v[1]))
			

	if outputFile=="":
		outputFile=fileName+".png"

	startRow=headerRow+1
	#headerRow-=1
	header,prestarts=getHeader(fileName,headerRow,startRow,fs)
		
	plotCols=getCol0ListFromCol1ListStringAdv(header,colString)

	#read in data
	toPlots=[]
	CDFs=[]

	for plotCol in plotCols:
		toPlots.append([header[plotCol],[]])

	
	fil=open(fileName)
	for lin in fil:
		fields=lin.strip().split(fs)
		for toPlota,plotCol in zip(toPlots,plotCols):
			try:			
				plotstring=fields[plotCol]
				if plotstring.lower()=='nan':
					raise ValueError
			
				data=float(plotstring)
			except:
				continue

			if not minFixed:
				minValue=min([data,minValue])
			if not maxFixed:
				maxValue=max([data,maxValue])
			toPlota[1].append(data)
			
		
	figure(figsize=(9,6)) 
	subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.7)

	binfreq=[]
	binthreshold=[]
	
	#compute binthresholds
	binSep=(maxValue-minValue)/numBins
	for i in range(0,numBins):
		binthreshold.append(minValue+binSep*i)

	binthreshold.append(maxValue)

	plots=[]
	labels=[]

	for plotName,plotData in toPlots:
		numDataPoints=len(plotData)
		k=plotData+binthreshold
		k.sort()
		CDF=[]
		CDFs.append(CDF)
		for bint in binthreshold:
			loct=k.index(bint)
			while loct<len(k) and k[loct]==bint: #until reaching the bigger value or end
				loct+=1
			loct-=1
			cdf=float(loct)/numDataPoints
			CDF.append(cdf)
			#print >> stderr,bint,cdf

			del k[loct]			
		
		plots.append(plot(binthreshold,CDF,label=plotName))
		labels.append(plotName)

	figlegend(plots,labels,'upper right')
	
	if YRangeFixed:
		ylim(YRange[0],YRange[1])

	savefig(outputFile,bbox_inches="tight")
