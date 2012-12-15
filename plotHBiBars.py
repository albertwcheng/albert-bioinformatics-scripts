#!/usr/bin/env python

import matplotlib.pyplot as plt
from albertcommon import *
from getopt import getopt
from sys import *
from math import *
import matplotlib.lines as mlines

def printUsageAndExit(programName):
	print >> stderr,programName,"[Options] Filename  LeftDataColumn  RightDataColumn OutFigName"
	print >> stderr,programName,"--single-col-mode [Options] Filename DataColumn OutFigName"
	print >> stderr,"Options:"
	print >> stderr,"--bar-height height. default:10"
	print >> stderr,"--left-face-color color. default:blue"
	print >> stderr,"--right-face-color color. default:red"
	print >> stderr,"--left-annot-col col.default:None"
	print >> stderr,"--right-annot-col col. default:None"
	print >> stderr,"--annot-delta delta. specify the label distance from the bar"
	print >> stderr,"--fig-width-delta. specify how much extra space to add on both sides"
	print >> stderr,"--font-size fontsize"
	print >> stderr,"--line-width lineWidth"
	print >> stderr,"--XLabel xLabel"
	print >> stderr,"--left-annot-only item1,item2, . . . ,itemN. Only annotate those items on left side"
	print >> stderr,"--right-annot-only item1,item2, . . . ,itemN. Only Annotation those items on right side"
	print >> stderr,"--single-col-mode. Plot single column putting positive on right, negative on left"
	#print >> stderr,"--sorted-reverse Sort the single col data"
	#print >> stderr,"--sorted Sort the single col data"
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['bar-height=','left-face-color=','right-face-color=','left-annot-col=','right-annot-col=','annot-delta=','fig-width-delta=','font-size=','line-width=','XLabel=','left-annot-only=','right-annot-only=','single-col-mode','sorted-reverse','sorted','annot-col=','annot-only='])
	
	leftFaceColor="blue"
	rightFaceColor="red"
	barHeight=10.0
	leftAnnotCol=None
	rightAnnotCol=None
	fontSize=16
	annotDelta=0.5
	figWidthDelta=1
	startRow=2
	headerRow=1
	XLabel="X"
	fs="\t"
	lineWidth=0
	leftAnnotOnly=None
	rightAnnotOnly=None
	singleColMode=False
	sortedflag=0
	for o,v in opts:
		if o=='--bar-height':
			barHeight=float(v)
		elif o=='--left-face-color':
			leftFaceColor=v
		elif o=='--right-face-color':
			rightFaceColor=v
		elif o=='--left-annot-col':
			leftAnnotCol=v
		elif o=='--right-annot-col':
			rightAnnotCol=v
		elif o=='--annot-delta':
			annotDelta=float(v)
		elif o=='--fig-width-delta':
			figWidthDelta=float(v)
		elif o=='--font-size':
			fontSize=float(v)
		elif o=='--line-width':
			lineWidth=float(v)
		elif o=='--XLabel':
			XLabel=v
		elif o=='--left-annot-only':
			leftAnnotOnly=v.split(",")
		elif o=='--right-annot-only':
			rightAnnotOnly=v.split(",")
		elif o=='--single-col-mode':
			singleColMode=True
		elif o=='--sorted-reverse':
			sortedflag=-1
		elif o=='--sorted':
			sortedflag=1
		elif o=='--annot-only':
			leftAnnotOnly=v.split(",")
		elif o=='--annot-col':
			leftAnnotCol=v
		
		
	rightDataCol=None
	
	if singleColMode:
		try:
			filename,leftDataCol,outFig=args
		except:
			printUsageAndExit(programName)
	else:
		try:
			filename,leftDataCol,rightDataCol,outFig=args
		except:
			printUsageAndExit(programName)
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	if leftAnnotCol:
		leftAnnotCol=getCol0ListFromCol1ListStringAdv(header,leftAnnotCol)[0]
	leftDataCol=getCol0ListFromCol1ListStringAdv(header,leftDataCol)[0]
	if rightAnnotCol:
		rightAnnotCol=getCol0ListFromCol1ListStringAdv(header,rightAnnotCol)[0]
	if rightDataCol:
		rightDataCol=getCol0ListFromCol1ListStringAdv(header,rightDataCol)[0]

	leftMax=0.0
	rightMax=0.0

	fig = plt.figure()
	ax = fig.add_subplot(111)
	
	leftAnnot=[]
	leftData=[]
	rightAnnot=[]
	rightData=[]
	
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		
		
		if singleColMode:
			try:
				X=float(fields[leftDataCol])
				if X>0:
					rightData.append(X)
					leftData.append(0.0)
					if leftAnnotCol!=None:
						if leftAnnotOnly==None or fields[leftAnnotCol] in leftAnnotOnly:
							rightAnnot.append(fields[leftAnnotCol])
						else:
							rightAnnot.append("")
						leftAnnot.append("")
				else:
					leftData.append(X)
					rightData.append(0.0)
					if leftAnnotCol!=None:
						if leftAnnotOnly==None or fields[leftAnnotCol] in leftAnnotOnly:
							leftAnnot.append(fields[leftAnnotCol])
						else:
							leftAnnot.append("")
						rightAnnot.append("")
								
			except:
				pass
		else:		
			try:
				leftData.append(float(fields[leftDataCol]))
				if leftAnnotCol!=None:
					if  leftAnnotOnly==None or fields[leftAnnotCol] in leftAnnotOnly:
						leftAnnot.append(fields[leftAnnotCol])
					else:
						leftAnnot.append("")
			except:
				leftData.append(0.0)
				if leftAnnotCol!=None:
					leftAnnot.append("")			
			
	
			try:
				rightData.append(float(fields[rightDataCol]))
				if rightAnnotCol!=None:
					if rightAnnotOnly==None or fields[rightAnnotCol] in rightAnnotOnly:
						rightAnnot.append(fields[rightAnnotCol])
					else:
						rightAnnot.append("")
			except:
				rightData.append(0.0)
				if rightAnnotCol!=None:
					rightAnnot.append("")			

		

		
		
		
	fil.close()
	
	cury=0
	
	for i in range(len(leftData)-1,-1,-1):
		rightV=fabs(rightData[i])
		ax.broken_barh([ (0, rightV)] , (cury, barHeight), linewidth=lineWidth, facecolors=(rightFaceColor)) #plot right
		leftV=fabs(leftData[i])
		ax.broken_barh([ (-leftV, leftV)] , (cury, barHeight), linewidth=lineWidth,facecolors=(leftFaceColor)) #plot left
		if leftAnnotCol!=None and len(leftAnnot[i])>0:
			ax.annotate(leftAnnot[i], (-leftV-annotDelta, cury+barHeight/2),fontsize=fontSize,horizontalalignment='right', verticalalignment='center')
			line = mlines.Line2D([-leftV-annotDelta/1.2,-leftV], [cury+barHeight/2,cury+barHeight/2])
			ax.add_line(line)
			#ax.arrow(-leftV-annotDelta/1.2, cury+barHeight/2, annotDelta/1.2 , 0, head_width=0.05, head_length=0.1, fc='k', ec='k')
		if rightAnnotCol!=None and len(rightAnnot[i])>0:
			ax.annotate(rightAnnot[i], (rightV+annotDelta, cury+barHeight/2),fontsize=fontSize,horizontalalignment='left', verticalalignment='center')
			line = mlines.Line2D([rightV+annotDelta/1.2,rightV], [cury+barHeight/2,cury+barHeight/2])
			ax.add_line(line)
			#ax.arrow(rightV+annotDelta/1.2, cury+barHeight/2, -annotDelta/1.2,0, head_width=0.05, head_length=0.1, fc='k', ec='k')
			
		leftMax=max(leftMax,leftV)
		rightMax=max(rightMax,rightV)
		
		cury+=barHeight
		
	ax.set_ylim(0,cury)

	ax.set_xlim(-leftMax-figWidthDelta,rightMax+figWidthDelta)
	ax.set_xlabel(XLabel)
	ax.set_yticks([])

	
	plt.savefig(outFig)