#!/usr/bin/env python

#derived from plotExpBox2.py
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
from sys import stderr,stdout,argv
from getopt import getopt
import sys
from albertcommon import *
from welchttest import welchs_approximate_ttest_arr
from scipy.stats.stats import ttest_ind,ttest_1samp,mannwhitneyu
from scipy.stats import wilcoxon #this is paired!!
from glob import glob
from random import *
from PZFXMaker import *
from scipy.stats import gaussian_kde
from numpy import arange

def plotExpBox(data,xtickLabels,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,xlegendrotation,xlabe,ylabe,titl,showSampleSizes,showViolin,showBox,annot,trendData,plotItemLegend,makePzfxFile):
	
	#fig=plt.figure()
	if plotItemLegend:
		ax2=subplot(122)
		ax=subplot(121)
	else:
		ax=gca()
	
	prevHoldState=ishold()	
	hold(True)
	
	if outliers:	
		fliers="b+"
	else:
		fliers=""

	whisValue=0.0

	if whisker:
		whisValue=1.5

	for i in range(0,len(data)):
		print >> stderr,len(data[i])

	if showBox:
		ax.boxplot(data,notch,widths=0.5,sym=fliers,whis=whisValue)
	#print >> stderr,resultD
	
	maxMax=-10000000.0
	minMin=10000000.0
	
	violinw=min(0.15*max(len(data)-1,1.0),0.5)

	if trendData:
		#print >> stderr,"plot"
		for trendDataStartIdx,trendDataForThisStartIdx in trendData.items():
			#print >> stderr,"plot",len(trendDataForThisStartIdx)
			trendcurves=[]
			legendlabels=[]
			if annot:
				annotForThisStartIdx=annot[trendDataStartIdx]
			for i in range(0,len(trendDataForThisStartIdx)):
				trendDataPerItem=trendDataForThisStartIdx[i]
				if annot:
					annotThisItem=annotForThisStartIdx[i]
				if trendDataPerItem:
					#print >> stderr,"plot"
					thisTrend=ax.plot(range(trendDataStartIdx+1,trendDataStartIdx+len(trendDataPerItem)+1),trendDataPerItem,"-")
					if annot and plotItemLegend:
						trendcurves.append(thisTrend)
						legendlabels.append(annotThisItem)
	
		
	for i in range(0,len(data)):
		curCol=data[i]
#		datasorted=data[:]
#		datasorted.sort()
#		numData=len(datasorted)
#		HQn=numData*3/4		
#		LQn=numData*1/4
#		maxMax=max(maxMax,datasorted[HQn]*1.5)
#		minMin=min(minMax,datasorted[LQn]*1.5)
			
		maxMax=max(maxMax,max(curCol))
		minMin=min(minMin,min(curCol))
		if showMean:
			ax.plot([i+0.75,i+1.25],[mean(curCol)]*2,markMean)
		
		
				
		if showIndPoints:
			plot([i+1]*len(curCol),curCol,mark)
		if showViolin:
			
			kernel=gaussian_kde(curCol)
			kernel_min=kernel.dataset.min()
			kernel_max=kernel.dataset.max()
			violinx=arange(kernel_min,kernel_max,(kernel_max-kernel_min)/100.) 
			violinv=kernel.evaluate(violinx)
			violinv=violinv/violinv.max()*violinw
			fill_betweenx(violinx,i+1,violinv+i+1,facecolor='y',alpha=0.3)
			fill_betweenx(violinx,i+1,-violinv+i+1,facecolor='y',alpha=0.3)						

	if showSampleSizes:
		for i in range(0,len(data)):
			curCol=data[i]
			text(i+1,maxMax*1.05,str(len(curCol)),horizontalalignment='center',verticalalignment='center',color='red')

			
	
	
	xticks( range(1,len(data)+1), xtickLabels , rotation=xlegendrotation)
	
	if makePzfxFile:
		
		
		pzfxTemplateFile,outFile,tableRefID=makePzfxFile
		#prepare data format
		PzfxData=[]
		for xtickLabel,dataCol in zip(xtickLabels,data):
			PzfxData.append( [xtickLabel, dataCol ] )
		writePzfxTableFile(outFile,pzfxTemplateFile,tableRefID,titl,80,3,PzfxData)
	
	xlabel(xlabe)
	ylabel(ylabe)
	title(titl)
	ylim([minMin-maxMax*0.1,maxMax*1.1])
	
	if plotItemLegend:
		box=ax.get_position()
		#gcf().set_figwidth(gcf().get_figwidth()*2)
		#ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		#subplots_adjust(top=0.8,bottom=0.1,left=0,right=0.8)
		
		#box2=ax2.get_position()
		#ax2.set_position([box2.x0,box2.y0, box.width * 0.1,box.height])
		subplots_adjust(top=0.8, bottom=0.1, left=0, right=0.8)
		leg=ax.legend(trendcurves,legendlabels,bbox_to_anchor=(1,0),loc="center left")
		#leg = gcf().get_legend()
		ltext  = leg.get_texts()
		
		
		plt.setp(ltext, fontsize=10)
	
	hold(prevHoldState)

def findIndices(needles,haystack):
	indices=[]
	for needle in needles:
		indices.append(haystack.index(needle))

	return indices

def rearrangeColAndRowSqMatrix(M,from_indices):
	newM=[]
	lenM=len(M)
	for r in range(0,lenM):
		newRow=[]
		newM.append(newRow)
		for c in range(0,lenM):
			newRow.append(M[from_indices[r]][from_indices[c]])

	return newM

def printMatrix(stream,M,prefixes):
	for row,prefix in zip(M,prefixes):
		for cell in row:
			print >> stream,"%g\t" % (cell),

		print >> stream,prefix
#use pvalue as a distance metric
#dist=1-pvalues
#fake the record for PyCluster
def makePValueClusterPlot(jobname,sampleNames,pvaluesM,methodCluster):



	#fake a record
	record=Record()
	#fake M
	M=[]
	Mr=[]
	M.append(Mr)
	for sample in sampleNames:
		Mr.append(0)

	record.data=M
	record.mask=None
	record.geneid=["Dummy"]
	record.genename=["Dummy"]
	record.expid=sampleNames
	record.uniqid="GENENAME"

	#now do something serious
	distM=[]
	for pvalueRows in pvaluesM:
		distRow=[]
		distM.append(distRow)
		for pvalue in pvalueRows:
			distRow.append(1.0-pvalue)

	
	#now cluster
	Tree=treecluster(distancematrix=distM,method=methodCluster)	

	record.save(jobname,expclusters=Tree)

	#now hijack the result file and change it to pvalue heatmap
	fil=open(jobname+".cdt")
	firstthreelines=[]
	lino=0
	for lin in fil:
		lino+=1
		if lino>3:
			break
		lin=lin.rstrip()
		firstthreelines.append(lin)
		if lino==1:
			fields=lin.split("\t")	
			arrayOrdered=fields[3:]
	


	fil.close()

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=rearrangeColAndRowSqMatrix(pvaluesM,findIndices(arrayOrdered,sampleNames))

	for i in range(0,len(arrayOrdered)):
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)):
			print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()
	

	fil=open(jobname+".mat","w")

	print >> fil, "Correlation Matrix (Not Clustered)"
	print >> fil,"\t".join(sampleNames)
	printMatrix(fil, pvaluesM, sampleNames)

	print >> fil, "Correlation Matrix (Clustered)"
	print >> fil,"\t".join(arrayOrdered)
	printMatrix(fil, rearrangedCorrMatrix, arrayOrdered)
	fil.close()


def makePValueRawPlot(jobname,sampleNames,pvaluesM):



	#fake a record
	record=Record()
	#fake M
	M=[]
	Mr=[]
	M.append(Mr)
	for sample in sampleNames:
		Mr.append(0)

	record.data=M
	record.mask=None
	record.geneid=["Dummy"]
	record.genename=["Dummy"]
	record.expid=sampleNames
	record.uniqid="GENENAME"

	#now do something serious


	record.save(jobname)

	#now hijack the result file and change it to pvalue heatmap
	fil=open(jobname+".cdt")
	firstthreelines=[]
	lino=0
	for lin in fil:
		lino+=1
		if lino>2:
			break
		lin=lin.rstrip()
		firstthreelines.append(lin)
		if lino==1:
			fields=lin.split("\t")	
			arrayOrdered=fields[3:]
	


	fil.close()

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=pvaluesM


	for i in range(0,len(arrayOrdered)):
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)):
			print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()
	



def trimData(plotData,size):
	for plotDataVector in plotData:
		shuffle(plotDataVector)
		del plotDataVector[size:len(plotDataVector)]


def drawHistogram(outfilename,plotData,xtickLabels,nbins=50):
	fig=figure(figsize=(8,len(plotData)*2))
	fig.subplots_adjust(top=0.8, bottom=0.1, left=0.2, right=0.8)

	for i,D,label in zip(range(0,len(plotData)),plotData,xtickLabels):
		ax = fig.add_subplot(len(plotData),1,i) #len(plotData),1,i
		ax.hist(D,nbins)
		ax.set_title(label)

	#fig.show()

	fig.savefig(outfilename,bbox_inches="tight")
	
def plotExpBox_Main(inputFiles,headers,valcols,outputFile,sep,startRow,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,plotPvalueCluster,outputClusterPrefix,methodCluster,xlegendrotation,xlabe,ylabe,figsz,titl,showSampleSizes,trimToMinSize,relabels,logb,plotHistogramToFile,plotMedianForGroups,botta,showViolin,showBox,firstColAnnot,plotTrend,showLegend,makePzfxFile):

	#if plotPvalueCluster:
		#if pvalue cluster is needed:
	#	from Bio.Cluster.cluster import *
	#	from Bio.Cluster import *
		#endif


	
	#the real deal!
	plotData=[]	
	xtickLabels=[]
	
	trendData={}
	annot={}
	
	minSize=-1

	for inputFile,header,cols in zip(inputFiles,headers,valcols):
		fin=generic_istream(inputFile)
		
		startIdx=len(plotData)
		
		if firstColAnnot:
			colAnnot=cols[0]
			cols=cols[1:]
			annotThisFile=[]
			annot[startIdx]=annotThisFile
		else:
			colAnnot=-1
			annotThisFile=None
			
		for col in cols:
			plotData.append([])
			xtickLabels.append(header[col])

		colIndices=range(startIdx,startIdx+len(cols))
		
		if plotTrend:
			#print >> stderr,"plotTrend"
			trendDataThisFile=[]
			trendData[startIdx]=trendDataThisFile
		else:
			trendDataThisFile=None
			
			
		lino=0
		for lin in fin:
			lino+=1
			if lino<startRow:
				continue		
			fields=lin.rstrip("\r\n").split(sep)
			
			if plotTrend:
				#print >> stderr,"a"
				trendDataThisLine=[]
			else:
				trendDataThisLine=None
			
			allDataOKThisLine=True
			
			if colAnnot>=0:
				annotThisFile.append(fields[colAnnot])
			
			for idx,col in zip(colIndices,cols):
				try:
					value=float(fields[col])
					if logb!=0:
						if value==0.0:
							raise ValueError
						value=log(value)/logb							
					plotData[idx].append(value)
					
					if plotTrend:
						trendDataThisLine.append(value)
						#print >> stderr,"value:",value
					
				except:
					allDataOKThisLine=False	
				
			if plotTrend:
				if allDataOKThisLine:
					trendDataThisFile.append(trendDataThisLine)
				else:
					trendDataThisFile.append(None)
			
		fin.close()
	
		
		if minSize==-1:
			minSize=len(plotData[idx]) #or startIDX?
		else:
			minSize=min([minSize,len(plotData[idx])])
		

	if trimToMinSize:
		print >> stderr,"trimming to min size =",minSize
		trimData(plotData,minSize)

	if len(relabels)>0:
		#if len(relabels)!=len(xtickLabels):
		#	print >> stderr,"relabels doesn't have the same length as original label vectors",xtickLabels,"=>",relabels
		#	exit()
		print >> stderr,xtickLabels
		print >> stderr,relabels
		for i,relabel in zip(range(0,len(relabels)),relabels):
			xtickLabels[i]=relabel
		
	
	for i in range(0,len(plotMedianForGroups)):
		plotMedianForGroups[i]=getCol0ListFromCol1ListStringAdv(xtickLabels,plotMedianForGroups[i])
			
	
	#drawing medians:
	medianToDraw=[]
	for mediangrouper in plotMedianForGroups:
		curD=[]		
		for c in mediangrouper:
			curD.extend(plotData[c])
		medianToDraw.append(median(curD))


	for c in range(len(plotData)-1,-1,-1):
		if len(plotData[c])==0:
			print >> stderr,xtickLabels[c],"discarded"
			del plotData[c]
			del xtickLabels[c]


	print >> stdout,"student t-test (1 sample; mean=0)"
	print >> stdout,"sample","mean","p-val"


	for x in range(0,len(plotData)):
		#print >> stderr, len(plotData[x])
		try:
			print >> stdout, xtickLabels[x],mean(plotData[x]),ttest_1samp(plotData[x],0)[1]
		except:
			print >> stdout, xtickLabels[x],"NA","NA"

	pvalueM=[]
	
	print >> stdout,""
	
	print >> stdout,"student t-test (2 samples)"
	print >> stdout,"p-val",
	for x in range(0,len(plotData)):
		print >> stdout,xtickLabels[x],
	
	print >> stdout,""

	for x in range(0,len(plotData)):
		pvalueRow=[]
		pvalueM.append(pvalueRow)
		print >> stdout, xtickLabels[x],
		for y in range(0,len(plotData)):
			if y<=x:
				print >> stdout, "",
				if x==y:
					pvalueRow.append(1.0)
				else:
					pvalueRow.append(pvalueM[y][x])
			else:
				try:
					pvalue=ttest_ind(plotData[x],plotData[y])[1]
				except:
					pvalue=1.0

				print >> stdout, str(pvalue),
				pvalueRow.append(pvalue)
		print >> stdout,"";	

	
	print >> stdout,""

	


	if plotPvalueCluster:
		makePValueRawPlot(outputClusterPrefix+"_t_raw",xtickLabels,pvalueM)
		makePValueClusterPlot(outputClusterPrefix+"_t",xtickLabels,pvalueM,methodCluster)

	pvalueM=[]

	print >> stdout,"welch t-test"
	print >> stdout,"p-val",
	for x in range(0,len(plotData)):
		print >> stdout,xtickLabels[x],
	
	print >> stdout,""
	for x in range(0,len(plotData)):
		pvalueRow=[]
		pvalueM.append(pvalueRow)
		print >> stdout, xtickLabels[x],
		for y in range(0,len(plotData)):
			if y<=x:
				print >> stdout, "",
				if x==y:
					pvalueRow.append(1.0)
				else:
					pvalueRow.append(pvalueM[y][x])
					
			else:
				pvalue=welchs_approximate_ttest_arr(plotData[x],plotData[y])[3]
				print >> stdout, str(pvalue),
				pvalueRow.append(pvalue)
		print >> stdout,"";

	

	if plotPvalueCluster:
		makePValueRawPlot(outputClusterPrefix+"_Welch_raw",xtickLabels,pvalueM)
		makePValueClusterPlot(outputClusterPrefix+"_Welch",xtickLabels,pvalueM,methodCluster)

	
	print >> stdout,""
	print >> stdout,"non-parametric (Mann-Whitney U)" #"non-parametric (Mann-Whitney U if larger n<=20 else Wilcoxon)"
	print >> stdout,"p-val",
	for x in range(0,len(plotData)):
		print >> stdout,xtickLabels[x],
	

	pvalueM=[]

	print >> stdout,""
	for x in range(0,len(plotData)):
		pvalueRow=[]
		pvalueM.append(pvalueRow)
		print >> stdout, xtickLabels[x],
		for y in range(0,len(plotData)):
			if y<=x:
				print >> stdout, "",
				if x==y:
					pvalueRow.append(1.0)
				else:
					pvalueRow.append(pvalueM[y][x])
			else:
				#if max(len(plotData[x]),len(plotData[y]))<=20:
				try:
					pvalue=mannwhitneyu(plotData[x],plotData[y])[1]*2				
				except:
					pvalue=1.0
				print >> stdout,pvalue, #mann-whiteney need to mul by 2 (one tail to two tail)
				pvalueRow.append(pvalue)
				#else:
				#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
		print >> stdout,"";	
	
	

	if plotPvalueCluster:
		makePValueRawPlot(outputClusterPrefix+"_U_raw",xtickLabels,pvalueM)
		makePValueClusterPlot(outputClusterPrefix+"_U",xtickLabels,pvalueM,methodCluster)
	
	figure(figsize=figsz)
	subplots_adjust(top=0.9, bottom=botta, left=0.2, right=0.8)
	
	if len(titl)==0:
		titl=outputFile


	plotExpBox(plotData,xtickLabels,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,xlegendrotation,xlabe,ylabe,titl,showSampleSizes,showViolin,showBox,annot,trendData,showLegend,makePzfxFile)
	
	#ylim([0,200])
	for m in medianToDraw:
		axhline(y=m,linestyle=':',color='gray')

	savefig(outputFile,bbox_inches="tight")

	if len(plotHistogramToFile)>0:
		drawHistogram(plotHistogramToFile,plotData,xtickLabels)
	

def mulArray(x,n):
	L=[]
	for i in range(0,n):
		L.append(x)

	return L

def usageExit(programName):
	print >> stderr,programName,"outputFile [ inputFile1 valCol1 inputFile2 valCol2 ...] "
	print >> stderr,"Options:"
	print >> stderr,"-t -F -d --fs seperator"
	print >> stderr,"-r --headerRow headerRow"
	print >> stderr,"-s --startRow startRow"
	print >> stderr,"-p --showIndPoints"
	print >> stderr,"-m --showMean"
	print >> stderr,"-n --notch"
	print >> stderr,"--first-col-annot first column of each valCol is annotation"
	print >> stderr,"--plot-trend draw trend curves per file"	
	print >> stderr,"--xtick-rotation degree"
	print >> stderr,"--offWhisker"
	print >> stderr,"--offOutliers"
	print >> stderr,"--pvalue-cluster-as prefix  make pvalue cluster heatmap using 1-pvalue as distance metric"
	print >> stderr,"--pvalue-cluster-method method   cluster using one of the following method for the pvalue cluster heatmap"
	print >> stderr,"--xlabel label"
	print >> stderr,"--ylabel label"
	print >> stderr,"--figsize w,h"
	print >> stderr,"--title title (default is filename)"
	print >> stderr,"--show-sample-sizes"
	print >> stderr,"--relabel-as label1,label2,label3,...  relabel the columns"
	print >> stderr,"--plot-hist filename"
	print >> stderr,"--plot-median-for-group cols"
	print >> stderr,"--log base"
	print >> stderr,"--show-legend"
	print >> stderr,"--out-pzfx intemplate,outfile"
	print >> stderr, "from PyCluster (see http://www.biopython.org/DIST/docs/api/Bio.Cluster.Record-class.html#treecluster)"
	print >> stderr, "method   : specifies which linkage method is used:"
	print >> stderr, "           method=='s': Single pairwise linkage"
	print >> stderr, "           method=='m': Complete (maximum) pairwise linkage (default)"
	print >> stderr, "           method=='c': Centroid linkage"
	print >> stderr, "           method=='a': Average pairwise linkage"
	explainColumns(stderr)

	sys.exit()

if __name__=='__main__':
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:s:pmn',['fs=','headerRow=','startRow=','showIndPoints','showMean','notch','offWhisker','offOutliers','pvalue-cluster-as=','pvalue-cluster-method=','xtick-rotation=','xlabel=','ylabel=','figsize=','title=','show-sample-sizes','trim-to-min-size','relabel-as=','plot-hist=','plot-median-for-group=','log=','bottom=','hide-violin','hide-box','plot-trend','first-col-annot','show-legend','out-pzfx=','pzfx-tableref-id='])

	headerRow=1
	startRow=2
	fs="\t"
	showIndPoints=False
	showMean=False
	whisker=True
	outliers=True
	notch=0
	logb=0
	plotHistogramToFile=""
	plotMedianForGroups=[]
	xlegendrotation=0
	makePvalueClusters=False
	pvalueClusterOutputPrefix=""
	pvalueClusterMethod="a"
	xlabe="Samples"
	ylabe="Values"
	titl=""
	figsz=(8,6)
	showSampleSizes=False
	botta=0.3
	filenames=[]
	valcols=[]
	headers=[]
	relabels=[]
	firstColAnnot=False
	plotTrend=False
	trimToMinSize=False
	showViolin=True
	showBox=True
	showLegend=False
	makePzfxFile=None
	pzfxTableRefID="Table0"
	#if len(args)!=3:
		
	#else:
	try:
		outputFile=args[0]

	
		for a,v in optlist:
			if a in ["-F","-t","-d","--fs"]:
				fs=replaceSpecialChar(v)
			elif a in ["-s","--startRow"]:
				startRow=int(v)
			elif a in ["-r","--headerRow"]:
				headerRow=int(v)
			elif a in ["-p","--showIndPoints"]:
				showIndPoints=True
			elif a in ["-m","--showMean"]:
				showMean=True
			elif a in ["-n","--notch"]:
				notch=1
			elif a in ["--offOutliers"]:
				outliers=False
			elif a in ["--offWhisker"]:
				whisker=False
			elif a in ["--pvalue-cluster-as"]:
				makePvalueClusters=True
				pvalueClusterOutputPrefix=v
			elif a in ["--pvalue-cluster-method"]:
				pvalueClusterMethod=v
			elif a in ["--xtick-rotation"]:
				xlegendrotation=int(v)
			elif a in ["--xlabel"]:
				xlabe=v
			elif a in ["--ylabel"]:
				ylabe=v
			elif a in ["--figsize"]:
				v=v.split(",")
				figsz=(int(v[0]),int(v[1]))
			elif a in ["--title"]:
				titl=v
			elif a in ["--show-sample-sizes"]:
				showSampleSizes=True
			elif a in ["--trim-to-min-size"]:
				trimToMinSize=True
			elif a in ["--relabel-as"]:
				print >> stderr,"v=",v
				relabels=v.split(",")
			elif a in ['--log']:
				logb=log(float(v))
			elif a in ['--plot-hist']:
				plotHistogramToFile=v
			elif a in ['--plot-median-for-group']:
				plotMedianForGroups.append(v)
			elif a in ['--bottom']:
				botta=float(v)
			elif a in ['--hide-violin']:
				showViolin=False
			elif a in ['--hide-box']:
				showBox=False
			elif a in ['--first-col-annot']:
				firstColAnnot=True
			elif a in ['--plot-trend']:
				plotTrend=True
			elif a in ['--show-legend']:
				showLegend=True
			elif a in ['--out-pzfx']:
				makePzfxFile=v.split(",")
	except:
		usageExit(programName)
	
	#print >> stderr,args
	for i in range(1,len(args),2):
		thisFilenames=glob(args[i])
		valcolstring=args[i+1]
		filenames.extend(thisFilenames)
		for filenam in thisFilenames:
			header,prestarts=getHeader(filenam,headerRow,startRow,fs)
			cols=getCol0ListFromCol1ListStringAdv(header,valcolstring)
			print >> stderr, thisFilenames, cols
			valcols.append(cols)
			headers.append(header)	
	
	if makePvalueClusters:
		from Bio.Cluster.cluster import *
		from Bio.Cluster import *
	
	
	if showLegend:
		figsz=(figsz[0]*2,figsz[1])
	
	
	if makePzfxFile:
		makePzfxFile+=[pzfxTableRefID]
	
	plotExpBox_Main(filenames,headers,valcols,outputFile,fs,startRow,showIndPoints,'b,','g--',showMean,notch,whisker,outliers,makePvalueClusters,pvalueClusterOutputPrefix,pvalueClusterMethod,xlegendrotation,xlabe,ylabe,figsz,titl,showSampleSizes,trimToMinSize,relabels,logb,plotHistogramToFile,plotMedianForGroups,botta,showViolin,showBox,firstColAnnot,plotTrend,showLegend,makePzfxFile)	
		
		
