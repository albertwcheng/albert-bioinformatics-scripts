#!/usr/bin/env python

import matplotlib.pyplot as plt
from albertcommon import *
from getopt import getopt
from sys import *
from math import *

def printUsageAndExit(programName):
	print >> stderr,programName,"[Options] Filename  LeftDataColumn  RightDataColumn OutFigName"
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
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['bar-height=','left-face-color=','right-face-color=','left-annot-col=','right-annot-col=','annot-delta=','fig-width-delta=','font-size=','line-width=','XLabel='])
	
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
		try:
			leftData.append(float(fields[leftDataCol]))
			if leftAnnotCol!=None:
				leftAnnot.append(fields[leftAnnotCol])
		except:
			leftData.append(0.0)
			if leftAnnotCol!=None:
				leftAnnot.append("")			
		try:
			rightData.append(float(fields[rightDataCol]))
			if rightAnnotCol!=None:
				rightAnnot.append(fields[rightAnnotCol])
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
		if leftAnnotCol!=None:
			ax.annotate(leftAnnot[i], (-leftV-annotDelta, cury+barHeight/2),fontsize=fontSize,horizontalalignment='right', verticalalignment='center')
		if rightAnnotCol!=None:
			ax.annotate(rightAnnot[i], (rightV+annotDelta, cury+barHeight/2),fontsize=fontSize,horizontalalignment='left', verticalalignment='center')
			
		leftMax=max(leftMax,leftV)
		rightMax=max(rightMax,rightV)
		
		cury+=barHeight
		
	ax.set_ylim(0,cury)

	ax.set_xlim(-leftMax-figWidthDelta,rightMax+figWidthDelta)
	ax.set_xlabel(XLabel)
	ax.set_yticks([])

	
	plt.savefig(outFig)