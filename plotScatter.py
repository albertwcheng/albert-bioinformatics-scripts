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

import sys
from albertcommon import *
from pylab import *

def loadToPlotGenes(fin,sep="="):
	
	toPlotGenes=dict()	
	
	try:
		
		for line in fin:
			line=line.strip();
			if(line=="_end_"):
				break;		
			fields=line.split(sep)
						
			eventID=fields[0]
			try:
				label=fields[1]
			except:
				label=""
			try:
				color=fields[2]			
			except:
				color="k"

			toPlotGenes[eventID]=[label,color,False]
		fin.close();	
	except IOError:
		print >> stderr, filename,"not openable";
	
	return toPlotGenes;

if __name__=="__main__":
	try:
		filename,IDCol,Psi1Col,Psi2Col,sam1Name,sam2Name,startRow,toPlotGenesFile,outputName=sys.argv[1:]
	except ValueError:
		print >> sys.stderr,"Usage","filename IDCol xCol yCol xLabel yLabel startRow WatchList outputName"
		sys.exit()

	headerRow=1
	fs="\t"
	
	header,prestart=getHeader(filename,headerRow,headerRow,fs)

	
	if IDCol!="-":	
		IDCol=getCol0ListFromCol1ListStringAdv(header,IDCol)[0]
	else:
		IDCol=-1
	
	Psi1Col=getCol0ListFromCol1ListStringAdv(header,Psi1Col)[0]	
	Psi2Col=getCol0ListFromCol1ListStringAdv(header,Psi2Col)[0]
	startRow=int(startRow)

	fil=generic_istream(filename)
	toPlotGenes=loadToPlotGenes(open(toPlotGenesFile))
	toPlotGenesWatch=toPlotGenes.keys()

	lino=0
	
	X=[]
	Y=[]

	xMarked=[]
	yMarked=[]
	marked=[]
	
	
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		lino+=1
		if lino<startRow:
			continue

		
		x=float(fields[Psi1Col])
		y=float(fields[Psi2Col])
		X.append(x)
		Y.append(y)

		if IDCol>=0:
			eventID=fields[IDCol]
			if eventID in toPlotGenesWatch:
				xMarked.append(x)
				yMarked.append(y)
				marked.append(toPlotGenes[eventID])
				toPlotGenes[eventID][2]=True

	fil.close()

	for ID,prop in toPlotGenes.items():
		label,color,plotted=prop
		if not plotted:
			print >> sys.stderr, ID,label,color,"not plotted"




	#now plot
	figure(figsize=(8,8))
	title("scatter plot for "+sam1Name+" and "+sam2Name)
	xlabel(sam1Name)
	ylabel(sam2Name)
	
		
	
	plot(X,Y,'.b')
	for xm,ym,markedprop in zip(xMarked,yMarked,marked):
		label,color,plotted=markedprop
		plot((xm,),(ym,),color+'o');
		text(xm,ym,label,{'color' : color});
	
	#now just plot
	plot([4,20],[4,20],'-',color='grey')	
	
	plot([4,18],[6,20],'-',color='grey')	
	plot([6,20],[4,18],'-',color='grey')
	
	plot([4,19],[5,20],'-',color='grey')	
	plot([5,20],[4,19],'-',color='grey')	
	#plot([0,1],[0,1],'-',color='grey')
	
	#xlim([0,1])
	#ylim([0,1])
	#
	
	savefig(outputName)


