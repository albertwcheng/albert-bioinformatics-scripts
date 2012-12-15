#!/usr/bin/env python

from albertcommon import *
from sys import *
from getopt import getopt
import re

def printUsageAndExit(programName):
	print >> stderr,programName,"filename styleSpecFile"
	print >> stderr,"styleSpecFile:"
	print >> stderr,"lines of <regex>tab<color:either hexcode or rgba(0-255,..,0.0-1.0)>tab<shapefx:circle,square,triangle>"
	#print >> stderr,"Options:"
	
	exit(1)

def square(stream,x,y,width,height,color):
	print >> stream,'<rect x="%d" y="%d" width="%d" height="%d" style="fill: %s" />' %(x,y,width,height,color)

def circle(stream,x,y,width,height,color):
	print >> stream,'<circle cx="%d" cy="%d" r="%d"  style="fill: %s" />' %(x+width/2,y+height/2,width/2,color)

def triangle(stream,x,y,width,height,color):
	print >> stream,'<polygon points="%d,%d %d,%d %d,%d" style="fill: %s" />' %(x+width/2,y,x+width,y+height,x,y+height,color)


def drawNothing(stream,x,y,width,height,color):
	pass

shapefx={"square":square,
		 "circle":circle,
		 "triangle":triangle}
	
def readGroupSpecFile(filename):
	groupSpec=[]
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		pattern,color,shape=lin.split("\t")
		groupSpec.append((re.compile(pattern),color,shapefx[shape]))
	fil.close()
	return groupSpec

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		filename,groupSpecFile=args
	except:
		printUsageAndExit(programName)
	
	fs="\t"
	groupSpec=readGroupSpecFile(groupSpecFile)
	
	print >> stdout, "<?xml version=\"1.0\" standalone=\"no\"?>"
	print >> stdout, "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\""
	print >> stdout, "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
	print >> stdout, "<svg width=\"100%\" height=\"100%\" version=\"1.1\""
	print >> stdout, "xmlns=\"http://www.w3.org/2000/svg\">"
	
	
	x=0
	y=0
	width=10
	height=10
	NAColor="#CCCCCC"
	NAShapefx=drawNothing
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)
		x=0
		for f in fields:
			colorSelected=NAColor
			shapeFxSelected=NAShapefx
			for regex,color,shapefx in groupSpec:
				if regex.search(f)!=None:
					#matched
					colorSelected=color
					shapeFxSelected=shapefx
					break
			shapefx(stdout,x,y,width,height,colorSelected)
			x+=width
		
		y+=height	
		
	
	fil.close()
	
	
	print >> stdout,"</svg>"