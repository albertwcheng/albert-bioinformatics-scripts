#!/usr/bin/env python

#uses pygooglechart module via Google Chart API (http://code.google.com/apis/chart/)
# http://pygooglechart.slowchop.com/
#requires network connection?

from pygooglechart import VennChart
from types import *
from sys import *
from os.path import basename
def twodigithex(I):
	hexString=hex(I)
	if hexString[0:2]!="0x":
		print >> stderr,"wrong hex conversion from",I,"to",hexString,"abort"
		exit(1)
	hexString=hexString[2:]
	if len(hexString)<2:
		hexString="0"+hexString
	
	return hexString.upper()
	

def drawTwoVenn(set1,set2,intersect,width,height,outfile,title=None,legend=None,indicateNumberInLegend=False,colors=None,htmlReport=None):
	chart=VennChart(width,height)
	chart.add_data([set1,set2,0,intersect])
	if title:
		chart.set_title(title)
	if legend:
	
	
		legendOut=legend[:]
			
		if indicateNumberInLegend:
			
			legendOut[0]=legend[0]+" ("+str(set1)+")"
			legendOut[1]=legend[1]+" ("+str(set2)+")"
		chart.set_legend(legendOut)
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
	
	if htmlReport:
		if not title:
			title=""
		if not legend:
			legend=["set1","set2"]
			
		fout = open(htmlReport,"w")
		print >> fout, '<html><head><title>%s</title></head><body><h1>%s</h1><table width=%d><tr><td colspan=2><img src="%s"></td></tr><tr bgcolor="#AAAAAA"><td>%s</td><td>%d</td></tr><tr><td>%s</td><td>%d</td></tr> <tr bgcolor="#AAAAAA">  <td>%s only</td><td>%d</td></tr> <tr><td>%s only</td><td>%d</td></tr> <tr bgcolor="#AAAAAA"> <td>%s &#x2229; %s</td><td>%d</td></tr> </body></html>' %(title,title,width,basename(outfile),legend[0],set1,legend[1],set2,legend[0],set1-intersect,legend[1],set2-intersect,legend[0],legend[1],intersect)
		fout.close()

def drawThreeVenn(set1,set2,set3,set1set2Intersect,set1set3Intersect,set2set3Intersect,allIntersect,width,height,outfile,title=None,legend=None,indicateNumberInLegend=False,colors=None,htmlReport=None):
	chart=VennChart(width,height)
	chart.add_data([set1,set2,set3,set1set2Intersect,set1set3Intersect,set2set3Intersect,allIntersect])
	if title:
		chart.set_title(title)
	if legend:
		legendOut=legend[:]
		
		if indicateNumberInLegend:
			legendOut[0]=legend[0]+" ("+str(set1)+")"
			legendOut[1]=legend[1]+" ("+str(set2)+")"
			legendOut[2]=legend[2]+" ("+str(set3)+")"
			
		chart.set_legend(legendOut)
		
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

	if htmlReport:
		fout = open(htmlReport,"w")
		set1only=set1-set1set2Intersect-set1set3Intersect+allIntersect
		set2only=set2-set1set2Intersect-set2set3Intersect+allIntersect
		set3only=set3-set1set3Intersect-set2set3Intersect+allIntersect
		
		if not title:
			title=""
		if not legend:
			legend=["set1","set2","set3"]
		
		print >> fout, '<html><head><title>%s</title></head><body><h1>%s</h1><table width=%d><tr><td colspan=2><img src="%s"></td></tr><tr bgcolor="#AAAAAA"><td>%s</td><td>%d</td></tr><tr><td>%s</td><td>%d</td></tr> <tr bgcolor="#AAAAAA">  <td>%s</td><td>%d</td></tr> <tr>  <td>%s only</td><td>%d</td></tr>  <tr bgcolor="#AAAAAA"> <td>%s only</td><td>%d</td> </tr>  <tr><td>%s only</td><td>%d</td> </tr> <tr bgcolor="#AAAAAA"> <td>%s &#x2229; %s</td><td>%d</td></tr> <tr> <td>%s &#x2229; %s</td><td>%d</td></tr> <tr bgcolor="#AAAAAA"> <td>%s &#x2229; %s</td><td>%d</td></tr> <tr> <td>%s &#x2229; %s &#x2229; %s </td><td>%d</td></tr> </body></html>' %(title,title,width,basename(outfile),legend[0],set1,legend[1],set2,legend[2],set3,legend[0],set1only,legend[1],set2only,legend[2],set3only,legend[0],legend[1],set1set2Intersect,legend[0],legend[2],set1set3Intersect,legend[1],legend[2],set2set3Intersect,legend[0],legend[1],legend[2],allIntersect)
		fout.close()


def testTwoVenn():
	drawTwoVenn(10,20,3,500,300,"testTwoVenn.png","Two venn testing",["A","B"],True,[[255,255,0],[0,255,255]],"testTwoVenn.htm")
	
def testThreeVenn():
	drawThreeVenn(100,80,60,30,30,30,10,500,300,"testThreeVenn.png","Three venn testing",["A","B","C"],True,[[255,255,0],[0,255,255],[255,0,0]],"testThreeVenn.htm")
	

def printUsageAndExit(programName):
	print >> stderr,programName,"--v2 set1 set2 set1AndSet2  [--out-png outfile] [--html-report htmlreport] [--l2 set1name set2name ] [--c2 set1color set2color ] [--int-num]"
	print >> stderr,programName,"--v3 set1 set2 set3 set1AndSet2 set1AndSet3 set2AndSet3 set1AndSet2AndSet3 [--out-png outfile] [--html-report htmlreport] [--l3 set1name set2name set3name ] [--c3 set1color set2color set3color ] [--int-num]"
	exit(1)

if __name__=='__main__':
	#testTwoVenn()
	#testThreeVenn()
	pass
	