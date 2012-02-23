#!/usr/bin/env python

#uses pygooglechart module via Google Chart API (http://code.google.com/apis/chart/)
# http://pygooglechart.slowchop.com/
#requires network connection?

from pygooglechart import VennChart
from types import *
from sys import *

def twodigithex(I):
	hexString=hex(I)
	if hexString[0:2]!="0x":
		print >> stderr,"wrong hex conversion from",I,"to",hexString,"abort"
		exit(1)
	hexString=hexString[2:]
	if len(hexString)<2:
		hexString="0"+hexString
	
	return hexString.upper()
	

def drawTwoVenn(set1,set2,intersect,width,height,outfile,title=None,legend=None,indicateNumberInLegend=False,colors=None):
	chart=VennChart(width,height)
	chart.add_data([set1,set2,0,intersect])
	if title:
		chart.set_title(title)
	if legend:
		if indicateNumberInLegend:
			legend[0]=legend[0]+" ("+str(set1)+")"
			legend[1]=legend[1]+" ("+str(set2)+")"
		chart.set_legend(legend)
	if colors:
		for i in range(0,len(colors)):
			if type(colors[i]) is not StringType:
				#probably a int tuple (4 or 3)
				#print >> stderr,colors[i],"is not string"
				if  type(colors[i]) is ListType or  type(colors[i]) is TupleType:
					#print >> stderr,"is list or tuple"
					hexCode=""
					for color_component in colors[i]:
						hexCode+=twodigithex(color_component)
					colors[i]=hexCode
		
		#print >> stderr,colors
		chart.set_colours(colors)
	
	chart.download(outfile)

def drawThreeVenn(set1,set2,set3,set1set2Intersect,set1set3Intersect,set2set3Intersect,allIntersect,width,height,outfile,title=None,legend=None,indicateNumberInLegend=False,colors=None):
	chart=VennChart(width,height)
	chart.add_data([set1,set2,set3,set1set2Intersect,set1set3Intersect,set2set3Intersect,allIntersect])
	if title:
		chart.set_title(title)
	if legend:
		if indicateNumberInLegend:
			legend[0]=legend[0]+" ("+str(set1)+")"
			legend[1]=legend[1]+" ("+str(set2)+")"
			legend[2]=legend[2]+" ("+str(set3)+")"
			
		chart.set_legend(legend)
		
	if colors:
		for i in range(0,len(colors)):
			if type(colors[i]) is not StringType:
				#probably a int tuple (4 or 3)
				#print >> stderr,colors[i],"is not string"
				if  type(colors[i]) is ListType or  type(colors[i]) is TupleType:
					#print >> stderr,"is list or tuple"
					hexCode=""
					for color_component in colors[i]:
						hexCode+=twodigithex(color_component)
					colors[i]=hexCode
		
		#print >> stderr,colors
		chart.set_colours(colors)
	
	chart.download(outfile)


def testTwoVenn():
	drawTwoVenn(10,10,5,500,300,"testTwoVenn.png","two venn testing",["A","B"],True,[[255,255,0],[0,255,255]])
	
def testThreeVenn():
	drawThreeVenn(100,80,60,30,30,30,10,500,300,"testThreeVenn.png","three venn testing",["A","B","C"],True,[[255,255,0],[0,255,255],[255,0,0]])
	

if __name__=='__main__':
	#testTwoVenn()
	#testThreeVenn()
	
	