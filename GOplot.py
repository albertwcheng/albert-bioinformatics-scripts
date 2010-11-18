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
from albertcommon import *
from getopt import getopt
import matplotlib.pyplot as plt
from math import log
from operator import itemgetter
from configobj import ConfigObj

#GOplot.py [options] GOTableFile GOTermCol LHCol LTCol PHCol PTCol pvalueCol outputFigName
# --plot-y-pvalue
# --plot-y-enrichment
# --sort-by-pvalue
# --sort-by-enrichment
# --reverse 

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] GOTableFile GOTermCol LHCol LTCol PHCol PTCol pvalueCol configFile outputFigName" 
	print >> stderr,"-s key=strvalue"
	print >> stderr,"-i key=intvalue"
	print >> stderr,"-f key=floatvalue"

	explainColumns(stderr)
	exit()



def plotOneHeadBarChart(GOData,settings):
	
	outputFigName=settings["outputFigName"]
	
	
	try:
		leftMax=settings["max"+settings["leftPlotKey"]]
	except:
		leftMax=-100

	try:	
		rightMax=settings["max"+settings["rightPlotKey"]]
	except:
		rightMax=-100

	
	
	
	leftColor=settings["leftColor"]
	rightColor=settings["rightColor"]
	
	
	

	fontSize=settings["fontSize"]

	
	
	try:
		fig = plt.figure(1,(settings["figdimwidth"],settings["figdimheight"]))
	except:
		fig = plt.figure(1)
	
	try:
		plt.subplots_adjust(left=settings["leftadjust"], right=settings["rightadjust"])
	except:
		pass
	
	ax=fig.add_subplot(111)
	
		

		
	YEach=settings["YWidth"]
	YSpace=settings["YSpacing"]
	
	

	leftYTicks=[]
	leftYLabels=[]
	
	

	rightYTicks=[]
	rightYLabels=[]


	leftBound=0
	rightBound=max([leftMax,rightMax])
	


	
	try:
		rightBound+=max([settings["leftSpacing"],settings["rightSpacing"]])
	except:
		pass


	try:
		rightBound*=max([settings["leftInflation"],settings["rightInflation"]])
	except:
		pass


	try:
		leftRightMaxInflation=settings["leftRightMaxInflation"]
		inflation=rightBound*(leftRightMaxInflation-1.0)
		rightBound+=inflation
	except:
		pass
	

	currentY=YSpace



	M=[]

	for GODataRowI in range(0,len(GOData)) :

		GODataRow=GOData[GODataRowI]
		
		if GODataRowI==0:
			Mrow=["Terms"]
			try:
				Mrow.append(settings["rightPlotKey"])
			except:
				pass

			try:
				Mrow.append(settings["leftPlotKey"])
			except:
				pass

			M.append(Mrow)

		origY=currentY
		Mrow=[GODataRow["GOTermNames"]]

		try:
						
			rightLength=GODataRow[settings["rightPlotKey"]]
			rightMin=0
			#print >> stderr, "found"
			
			Mrow.append(str(rightLength))

			

			ax.broken_barh([(rightMin,rightLength)],(currentY,YEach), facecolors=(rightColor)) 
			
			
			try:	
				rightCenterLabel=str(GODataRow[settings["rightInBarLabelKey"]])
				ax.text(rightLength/2, currentY+YEach/2, rightCenterLabel, horizontalalignment="center",verticalalignment='center', size=fontSize, color="black")
			except:
				pass

			try:
				rightBarRightLabel=" "+str(GODataRow[settings["rightBarRightLabelKey"]])
				ax.text(rightLength, currentY+YEach/2, rightBarRightLabel, horizontalalignment="left",verticalalignment='center', size=fontSize, color="black")
			except:
				pass


			currentY+=YEach

		except:
			pass


		try:
			leftLength=GODataRow[settings["leftPlotKey"]]
			leftMin=0		
			
			Mrow.append(str(leftLength))

			ax.broken_barh([(leftMin,leftLength)],(currentY,YEach), facecolors=(leftColor)) 
			
			try:
				leftCenterLabel=str(GODataRow[settings["leftInBarLabelKey"]])
				ax.text(leftLength/2, currentY+YEach/2, leftCenterLabel, horizontalalignment="center",verticalalignment='center', size=fontSize, color="black")
			except:
				pass

			try:
				leftBarLeftLabel=" "+str(GODataRow[settings["leftBarLeftLabelKey"]])
				ax.text(leftLength, currentY+YEach/2, leftBarLeftLabel, horizontalalignment="left",verticalalignment='center', size=fontSize, color="black")
			except:
				pass
	
			currentY+=YEach
			
		except:
			pass

		M.append(Mrow)



		try:
			leftYLabels.append(GODataRow[settings["leftYLabelKey"]])
			leftYTicks.append((currentY+origY)/2)
		except:
			pass

		try:
			rightYLabels.append(GODataRow[settings["rightYLabelKey"]])
			rightYTicks.append((currentY+origY)/2)
		except:
			pass

		
		currentY+=YSpace

		
	



	ax.set_yticks(leftYTicks) #left
	ax.set_yticklabels(leftYLabels)

	ax.plot([0,0], [0, currentY+YEach], 'black' )

	ax2 = ax.twinx()
	ax2.set_yticks(rightYTicks)
	ax2.set_yticklabels(rightYLabels)
	

	#try:
	#	balanceLeftRightXMax=settings["balanceLeftRightXMax"]
	#	if balanceLeftRightXMax:
	#		maxLRBound=max([abs(leftBound),abs(rightBound)])
	#		leftBound=-1*maxLRBound
	#		rightBound=maxLRBound
	#except:
	#	pass
	
	ax.set_xlim(leftBound,rightBound)



	ax.set_ylim(0,currentY)
	ax2.set_ylim(0,currentY)

	try:
		ax.set_ylabel(settings["leftYLabel"])
	except:
		pass

	try:
		ax2.set_ylabel(settings["rightYLabel"])
	except:
		pass


	try:
		ax.set_xlabel(settings["XLabel"])
	except:
		pass

	
	try:
		ax2.set_title(settings["Title"])
	except:
		pass

	#now output M

	for mrow in M:
		print >> stdout,"\t".join(mrow)



	
	if outputFigName!="-":
		plt.savefig(outputFigName)
	else:
		plt.show()
	

def plotTwoHeadBarChart(GOData,settings):
	
	outputFigName=settings["outputFigName"]
	
	

	leftPlotKey=settings["leftPlotKey"]
	rightPlotKey=settings["rightPlotKey"]
	
	leftMax=settings["max"+leftPlotKey]
	rightMax=settings["max"+rightPlotKey]

	
	
	
	leftColor=settings["leftColor"]
	rightColor=settings["rightColor"]
	
	
	

	fontSize=settings["fontSize"]

	
	
	try:
		fig = plt.figure(1,(settings["figdimwidth"],settings["figdimheight"]))
	except:
		fig = plt.figure(1)
	
	try:
		plt.subplots_adjust(left=settings["leftadjust"], right=settings["rightadjust"])
	except:
		pass
	
	ax=fig.add_subplot(111)
	
		

		
	YEach=settings["YWidth"]
	YSpace=settings["YSpacing"]
	
	

	leftYTicks=[]
	leftYLabels=[]
	
	

	rightYTicks=[]
	rightYLabels=[]


	leftBound=-1*leftMax
	rightBound=rightMax

	try:
		leftBound-=settings["leftSpacing"]
	except:
		pass
	
	try:
		rightBound+=settings["rightSpacing"]
	except:
		pass

	try:
		leftBound*=settings["leftInflation"]
	except:
		pass

	try:
		rightBound*=settings["rightInflation"]
	except:
		pass


	try:
		leftRightMaxInflation=settings["leftRightMaxInflation"]
		maxMax=max([abs(leftBound),abs(rightBound)])
		inflation=maxMax*(leftRightMaxInflation-1.0)
		leftBound-=inflation
		rightBound+=inflation
	except:
		pass
	
	
	maxY=-100
	

	M=[]

	for GODataRowI in range(0,len(GOData)) :

		GODataRow=GOData[GODataRowI]
		
		if GODataRowI==0:
			Mrow=["Terms"]
			try:
				Mrow.append(settings["rightPlotKey"])
			except:
				pass

			try:
				Mrow.append(settings["leftPlotKey"])
			except:
				pass

			M.append(Mrow)


		try:
			YPlotKey=settings["YPlotKey"]
			currentY=GODataRow[YPlotKey]					
		except:
			currentY=YSpace+(YSpace+YEach)*GODataRowI

		try:
			leftYLabels.append(GODataRow[settings["leftYLabelKey"]])
			leftYTicks.append(currentY+YEach/2)
		except:
			pass

		try:
			rightYLabels.append(GODataRow[settings["rightYLabelKey"]])
			rightYTicks.append(currentY+YEach/2)
		except:
			pass
		
		leftLength=GODataRow[leftPlotKey]
		leftMin=-1*(leftLength)

		rightLength=GODataRow[rightPlotKey]
		rightMin=0


		M.append([GODataRow["GOTermNames"],str(rightLength),str(leftLength)])

		
		ax.broken_barh([(leftMin,leftLength),(rightMin,rightLength)],(currentY,YEach), facecolors=(leftColor,rightColor)) 
		
		try:
			leftCenterLabel=str(GODataRow[settings["leftInBarLabelKey"]])
			ax.text(leftMin/2, currentY+YEach/2, leftCenterLabel, horizontalalignment="center",verticalalignment='center', size=fontSize, color="black")
		except:
			pass
		
		try:
			rightCenterLabel=str(GODataRow[settings["rightInBarLabelKey"]])
			ax.text(rightLength/2, currentY+YEach/2, rightCenterLabel, horizontalalignment="center",verticalalignment='center', size=fontSize, color="black")
		except:
			pass


		try:
			rightBarRightLabel=" "+str(GODataRow[settings["rightBarRightLabelKey"]])
			ax.text(rightLength, currentY+YEach/2, rightBarRightLabel, horizontalalignment="left",verticalalignment='center', size=fontSize, color="black")
		except:
			pass

		try:
			leftBarLeftLabel=str(GODataRow[settings["leftBarLeftLabelKey"]])+" "
			ax.text(leftMin, currentY+YEach/2, leftBarLeftLabel, horizontalalignment="right",verticalalignment='center', size=fontSize, color="black")
		except:
			pass

		maxY=max([maxY,currentY])
	
	ax.set_yticks(leftYTicks) #left
	ax.set_yticklabels(leftYLabels)



	ax.plot([0,0], [0, maxY+YEach+YSpace], 'black' )

	try:
		balanceLeftRightXMax=settings["balanceLeftRightXMax"]
		if balanceLeftRightXMax:
			maxLRBound=max([abs(leftBound),abs(rightBound)])
			leftBound=-1*maxLRBound
			rightBound=maxLRBound
	except:
		pass


	try:
		ax.text(leftBound/2, maxY+YEach+YSpace, settings["leftAreaHeadTitle"], horizontalalignment="center",verticalalignment='top', size=fontSize, color=leftColor)
	except:
		pass

	try:
		ax.text(rightBound/2, maxY+YEach+YSpace, settings["rightAreaHeadTitle"], horizontalalignment="center",verticalalignment='top', size=fontSize, color=rightColor)
	except:
		pass
	try:

		ax.text(leftBound/2, 0, settings["leftAreaBottomTitle"], horizontalalignment="center",verticalalignment='bottom', size=fontSize, color=leftColor)
	except:
		pass

	try:
		ax.text(rightBound/2, 0, settings["rightAreaBottomTitle"], horizontalalignment="center",verticalalignment='bottom', size=fontSize, color=rightColor)
	except:
		pass

		#print >> stderr,labels[i].text
		#print >> stderr,labels[i].label
		#print >> stderr, labeltext
		#print >> stderr,"got orig labeltext", labeltext
		#if labeltext[0]=='-':
		#	labeltext=labeltext[1:len(labeltext)]

		#labels[i].set_text(labeltext)

		#newxlabels.append(labeltext)
		
	#ax.set_xticks([-60,-40,-20,0,20,40,60])
	#ax.set_xticklabels(("60","40","20","0","20","40","60"))
	



	ax2 = ax.twinx()

	#try:
	#	if settings["rightYLabelKey"]=="default":
	#		pass
	#	else:
	#		ax2.set_yticks(rightYTicks)
	#		ax2.set_yticklabels(rightYLabels)
	#				
	#except:
	if "rightYLabelKey" in settings and  settings["rightYLabelKey"]=="default":
		pass
	else:
		ax2.set_yticks(rightYTicks)
		ax2.set_yticklabels(rightYLabels)
	


	
	ax.set_xlim(leftBound,rightBound)
	ax2.set_xlim(leftBound,rightBound)
	
	
	ax.set_ylim(0,maxY+YEach+YSpace)
	ax2.set_ylim(0,maxY+YEach+YSpace)
	
	
	locs= ax.get_xticks()
	
	newxlabels=[]
	for loc in locs:
		
		newxlabels.append(str(abs(loc)))
		
	
	ax.set_xticks(locs)
	ax.set_xticklabels(newxlabels)
	ax2.set_xticks(locs)
	ax2.set_xticklabels(newxlabels)
	ax2.xaxis.set_visible(False)

	try:
		ax.set_ylabel(settings["leftYLabel"])
	except:
		pass

	try:
		ax2.set_ylabel(settings["rightYLabel"])
	except:
		pass


	try:
		ax.set_xlabel(settings["XLabel"])
	except:
		pass

	
	try:
		ax2.set_title(settings["Title"])
	except:
		pass

	#now output M

	for mrow in M:
		print >> stdout,"\t".join(mrow)



	if outputFigName!="-":
		plt.savefig(outputFigName)
	else:
		plt.show()

	
def sortGOData(GOData,sortBy,reverseSort=False):
	GOData.sort(key=itemgetter(sortBy),reverse=reverseSort)

def GOPlot(settings, GOTableFile, GOTermCol, LHCol, LTCol, PHCol, PTCol, pvalueCol, outputFigName, fs, startRow,plotYpvalue,plotYenrichment,sortByPvalue, sortByEnrichment):

	GOData=[]
	fil=open(GOTableFile)

	maxLH=-100
	maxPHminusLH=-100
	maxPH=-100
	maxLHp=-100
	maxPHp=-100
	maxnlog10pvalue=-1000000
	
	#mode="oneHead"
	
	logbase=10
	
	try:
		logbase=settings["logbase"]
	except:
		pass


	lino=0
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue

		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)	
		GOTermNames=":".join(getSubvector(fields,GOTermCol))
		LH=int(fields[LHCol])
		LT=int(fields[LTCol])
		PH=int(fields[PHCol])
		PT=int(fields[PTCol])
		pvalue=float(fields[pvalueCol])
		LHp=float(LH)/LT*100
		PHp=float(PH)/PT*100
		nlog10pvalue=-1*log(pvalue,logbase)
		PHminusLH=PH-LH #the blue part
		foldEnrichment=LHp/PHp
		foldEnrichment1f="%.1f" % (foldEnrichment)
		pvalue1e="%.1e" % (pvalue)
		nlog10pvalue1f="%.1f" %(nlog10pvalue)
		LHp1f="%.1f" % (LHp)
		PHp1f="%.1f" % (PHp)
		LHp1f+="%"
		PHp1f+="%"
		
		GODataRow={"GOTermNames":GOTermNames,"LH":LH,"LT":LT,"PH":PH,"PT":PT,"pvalue":pvalue,"LHp":LHp,"PHp":PHp,"foldEnrichment":foldEnrichment,"PHminusLH":PHminusLH,"nlog10pvalue":nlog10pvalue,"foldEnrichment.1f":foldEnrichment1f,"nlog10pvalue.1f":nlog10pvalue1f,"pvalue.1e":pvalue1e}
		GODataRow["LHp.1f"]=LHp1f
		GODataRow["PHp.1f"]=PHp1f

		GOData.append(GODataRow)	
		maxLH=max([maxLH,LH])
		maxPHminusLH=max([maxPHminusLH,PHminusLH])
		maxPH=max([maxPH,PH])
		maxPHp=max([maxPHp,PHp])
		maxLHp=max([maxLHp,LHp])
		maxnlog10pvalue=max([maxnlog10pvalue,nlog10pvalue])
	fil.close()



	#setting row
	settings["maxLH"]=maxLH
	settings["maxPHminusLH"]=maxPHminusLH
	settings["maxPH"]=maxPH
	settings["maxPHp"]=maxPHp
	settings["maxLHp"]=maxLHp
	settings["maxnlog10pvalue"]=maxnlog10pvalue
	settings["outputFigName"]=outputFigName


	mode=settings["mode"]
	reverse=settings["reverse"]
	sortby=settings["sortby"]

	

	#for LH PHminusLH
	if 0:
		settings["leftPlotKey"]="LH"
		settings["rightPlotKey"]="PHminusLH"
		settings["leftInBarLabelKey"]="LH"
		settings["rightInBarLabelKey"]="PHminusLH"
		settings["leftBarLeftLabelKey"]="LHp.1f"
		settings["rightBarRightLabelKey"]="PHp.1f"
		settings["leftYLabelKey"]="GOTermNames"
		settings["rightYLabelKey"]="foldEnrichment.1f"
		settings["balanceLeftRightXMax"]=False
		
		sortby="foldEnrichment"
		reverse=False

		mode="twoHead"


	#for LHp PHp
	if 0:
		settings["leftPlotKey"]="LHp"
		settings["rightPlotKey"]="PHp"
		#settings["leftInBarLabelKey"]="LHp.1f"
		#settings["rightInBarLabelKey"]="PHp.1f"
		settings["leftBarLeftLabelKey"]="LHp.1f"
		settings["rightBarRightLabelKey"]="PHp.1f"
		#settings["rightBarRightLabelKey"]="pvalue.1e"
		settings["leftYLabelKey"]="GOTermNames"
		#settings["rightYLabelKey"]="default"
		settings["rightYLabelKey"]="foldEnrichment.1f"
		#settings["rightYLabelKey"]="nlog10pvalue.1f"
		settings["balanceLeftRightXMax"]=False
		#settings["YPlotKey"]="nlog10pvalue"
		settings["YWidth"]=5
		sortby="foldEnrichment"
		reverse=False


		mode="twoHead"



	#for nlog10pvalue
	if 0:
		settings["rightPlotKey"]="nlog10pvalue"
		mode="oneHead"



	


	sortGOData(GOData,sortby,reverse)


	if mode=="twoHead":
		plotTwoHeadBarChart(GOData,settings)
	elif mode=="oneHead":	
		plotOneHeadBarChart(GOData,settings)
	else:
		print >> stderr,"unknown mode",mode,".Abort"
		exit()

if __name__=="__main__":
	programName=argv[0]

	fs="\t"
	startRow=-1
	headerRow=1
	plotYpvalue=False
	plotYenrichment=False
	sortByPvalue=False
	sortByEnrichment=True
	reverseSort=False
	

	try:
		opts,args=getopt(argv[1:],'s:i:f:',[])
		GOTableFile, GOTermCol, LHCol, LTCol, PHCol, PTCol, pvalueCol, configFileName,outputFigName=args
	except:
		printUsageAndExit(programName)

	settings=dict()

	settings["figdimwidth"]=20
	settings["figdimheight"]=9
	settings["leftadjust"]=0.3
	settings["rightadjust"]=0.8
	settings["leftColor"]="red"
	settings["rightColor"]="cyan"
	settings["YWidth"]=10
	settings["YSpacing"]=5
	settings["fontSize"]=10
	settings["leftRightMaxInflation"]=1.1	


	configSettings=ConfigObj(configFileName)
	configSettingsDict=configSettings.dict()

	for o,v in configSettingsDict.items():
		o=o.split(":")
		if len(o)>1:
			if o[1]=="integer":
				v=int(v)
			elif o[1]=="float":
				v=float(v)	
	
		
		o=o[0]
	
		settings[o]=v
	

	for o,v in opts:
		vsplits=v.split("=")
		if o=="-i":
			settings[vsplits[0]]=int(vsplits[1])		
		elif o=="-f":
			settings[vsplits[0]]=float(vsplits[1])
		elif o=="-s":
			settings[vsplits[0]]=vsplits[1]

	ambparams=0

	if sortByEnrichment:
		ambparams+=1
	
	if sortByPvalue:
		ambparams+=1
	
	if plotYpvalue:
		ambparams+=1

	if plotYenrichment:
		ambparams+=1
	
	if ambparams!=1:
		print >> stderr,"one and only one of --plot-y-pvalue --plot-y-enrichment --sort-by-pvalue --sort-by-enrichment need to be set. Abort"
		exit()


	if startRow==-1:
		startRow=headerRow+1


	header,prestarts=getHeader(GOTableFile,headerRow,startRow,fs)

	GOTermCol=getCol0ListFromCol1ListStringAdv(header,GOTermCol)
	LHCol=getCol0ListFromCol1ListStringAdv(header,LHCol)[0]
	LTCol=getCol0ListFromCol1ListStringAdv(header,LTCol)[0]
	PHCol=getCol0ListFromCol1ListStringAdv(header,PHCol)[0]
	PTCol=getCol0ListFromCol1ListStringAdv(header,PTCol)[0]	
	pvalueCol=getCol0ListFromCol1ListStringAdv(header,pvalueCol)[0]

	GOPlot(settings,GOTableFile, GOTermCol, LHCol, LTCol, PHCol, PTCol, pvalueCol, outputFigName, fs, startRow,plotYpvalue,plotYenrichment,sortByPvalue, sortByEnrichment)
	

