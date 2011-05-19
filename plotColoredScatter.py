#!/usr/bin/env python

from pylab import *
from albertcommon import *
from sys import *
from getopt import getopt

'''
NUM_COLORS = 22

cm = get_cmap('gist_rainbow')
for i in range(NUM_COLORS):
    color = cm(1.*i/NUM_COLORS)  # color will now be an RGBA tuple

# or if you really want a generator:
cgen = (cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS))
'''

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] outName"
	
	print >> stderr,"[--fs t=tab] [--headerRow x=1] [--startRow y=2] [--xcol x=2] [--ycol y=3] [--labelcol L=1] [--config configfile] --file filename. Plot filename data with "
	print >> stderr,"\t--fs t. set field separator"
	print >> stderr,"\t--headerRow x. set header row"
	print >> stderr,"\t--startRow y. set data start row"
	print >> stderr,"\t--xcol xcol"
	print >> stderr,"\t--ycol ycol"
	print >> stderr,"\t--config configfile. load config file"
	exit(1)

startRow=2
headerRow=1
fs="\t"
xcol=2
ycol=3
labelcol=1
configfile=None
filename=None

def reinitLoadingParams():
	global startRow,headerRow,fs,xcol,ycol,labelcol,configfile,filename
	startRow=2
	headerRow=1
	fs="\t"
	xcol="2"
	ycol="3"
	labelcol="1"
	configfile=None
	filename=None

def toFloatArray(L):
	F=[]
	for s in L:
		F.append(float(s))
	return F
	
def plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs):
	# !groupDivider	.
	# !groupNameComponent	1-_1
	# !hasGroup	no
	# MATRIX ATTR rgbColor r,g,b
	# MATRIX ATTR colorMapColor colorMapName:indx[0.0-1.0]
	hasGroup=(getAttrWithDefaultValue(attrMatrix,"!hasGroup","no").lower()=="yes")
	groupDivider=getAttrWithDefaultValue(attrMatrix,"!groupDivider",".")
	groupNameComponent=getAttrWithDefaultValue(attrMatrix,"!groupNameComponent","1")
	defaultColor=toFloatArray(getAttrWithDefaultValue(attrMatrix,"!color",(0.0,0.0,0.0,1.0)))
	defaultMarkerStyle=getAttrWithDefaultValue(attrMatrix,"!markerStyle","o")
	defaultLineWidth=float(getAttrWithDefaultValue(attrMatrix,"!lineWidth",1))
	defaultMarkerSize=float(getAttrWithDefaultValue(attrMatrix,"!markerSize",1))
	defaultShowLabel=getAttrWithDefaultValue(attrMatrix,"!showLabel","no").lower()
	
	X=[]
	Y=[]
	labels=[]
	groups=dict()
	
	fil=open(filename)
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		if lino<startRow:
			continue
		fields=lin.split(fs)
		label=fields[labelcol]
		labels.append(label)
		x=float(fields[xcol])
		y=float(fields[ycol])
		X.append(x)
		Y.append(y)
		if hasGroup:
			#which group is this label?
			labelon=label.split(groupDivider)
			groupName=groupDivider.join(getSubvector(labelon,getCol0ListFromCol1ListStringAdv(labelon,groupNameComponent)))
			try:
				groupLabels,groupX,groupY=groups[groupName]
			except KeyError:
				groupLabels=[]
				groupX=[]
				groupY=[]
				groups[groupName]=(groupLabels,groupX,groupY)
			
			groupLabels.append(label)
			groupX.append(x)
			groupY.append(y)
		
					
	fil.close()
	
	#now plot
	if not hasGroup:
		groups["___default___"]=(labels,x,y)
	
	for groupName,groupData in groups.items():
		groupLabels,groupX,groupY=groupData
		markerStyle=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerStyle",defaultMarkerStyle)
		
		#for color, either rgbcolor or colormapcolor:
		rgbacolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"RGBAColor",None)
		colormapcolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"colorMapColor",None)
		lineWidth=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"lineWidth",defaultLineWidth))
		markerSize=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerSize",defaultMarkerSize))
		showLabel=(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showLabel",defaultShowLabel).lower()=="yes")
		if rgbacolor:
			_r,_g,_b,_a=toFloatArray(rgbacolor.split(","))
		elif colormapcolor:
			colormapName,idx=colormapcolor.split(":")
			_r,_g,_b,_a=get_cmap(colormapName)(float(idx))
		else:
			_r,_g,_b,_a=defaultColor
		
		plot(groupX,groupY,markerStyle,color=(_r,_g,_b),alpha=_a,linewidth=lineWidth,markersize=markerSize)
		
		if showLabel:
			for label,x,y in zip(groupLabels,groupX,groupY):
				text(x,y,label)
				
if __name__=='__main__':
	programName=argv[0]
	if len(argv[1:])<1:
		printUsageAndExit(programName)
	
	
	reinitLoadingParams()
	

	
	opts,args=getopt(argv[1:],'',['fs=','headerRow=','startRow=','xcol=','ycol=','labelcol=','config=','file='])

	try:
		outName,=args
	except:
		printUsageAndExit(programName)
	
	for o,v in opts:
		if o=='--fs':
			fs=v
		elif o=='--headerRow':
			headerRow=int(v)
		elif o=='--startRow':
			startRow=int(v)
		elif o=='--xcol':
			xcol=v
		elif o=='--ycol':
			ycol=v
		elif o=='--labelcol':
			labelcol=v
		elif o=='--config':
			configfile=v
		elif o=='--file':
			filename=v
			header,prestarts=getHeader(filename,headerRow,startRow,fs)	
			labelcol=getCol0ListFromCol1ListStringAdv(header,labelcol)[0]
			xcol=getCol0ListFromCol1ListStringAdv(header,xcol)[0]
			ycol=getCol0ListFromCol1ListStringAdv(header,ycol)[0]
			
			if configfile:
				attrMatrix=readNamedAttrMatrix(configfile)
			else:
				attrMatrix=dict()
			plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs)
			
			#after everything
			reinitLoadingParams()
			
		
	savefig(outName)
	
	
