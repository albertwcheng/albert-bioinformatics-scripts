#!/usr/bin/env python
# collapse samples!
#
#
#
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

from getopt import getopt,GetoptError
from sys import stderr,stdout
from albertcommon import *
import sys

exceptionStrFloatCalled=False

def exceptionStrFloat(S):
	
	global exceptionStrFloatCalled
	if exceptionStrFloatCalled:
		return
	
	exceptionStrFloatCalled=True
	print >> sys.stderr,"Warning: String Conversion Exception ["+S+"]"

	#print >> sys.stderr,	suppressStrFloatErrorAbortion
	suppressStrFloatErrorAbortion=False
	if not suppressStrFloatErrorAbortion:
		print >> sys.stderr,"aborted"
		sys.exit()

def StrVector2FloatVector(ListOfStr):
	FloatVector=[]
	for S in ListOfStr:
		try:
			FloatVector.append(float(S))
		except:
			exceptionStrFloat(S)
			

	return FloatVector



def calculateGroupValue(fields,cols0,method):
	
	groupV=selectListByIndexVector(fields,cols0)
	groupVF=StrVector2FloatVector(groupV)
	
	if method in ["meanRO","medianRO","minRO","maxRO"]:
		removeOutliers(groupVF)	

	if method in ["mean","meanRO"]:
		return meanOfList(groupVF)
	elif method in ["median","medianRO"]:
		return medianOfList(groupVF)
	elif method in ["max","maxRO"]:
		return percentileOfList(1.0,groupVF)
	elif method in ["min","minRO"]:
		return percentileOfList(0.0,groupVF)
	else:
		print >> stderr,"Method",method,"not found, aborting"
		sys.exit()

def collapseSamples_Main(filename,prefix,suffix,method,groupMethodMap,groupColsMap,colsGroupMap,includes0,fs,ofs):
	fin=generic_istream(filename)
	
	lino=0
	colIndx=range(0,len(includes0))

	for line in fin:
		lino+=1		
		line=line.strip("\r\n")
		fields=line.split(fs)
		outputFields=[]
		
		if lino==headerRow:
			for col0,include,field in zip(colIndx,includes0,fields):
				if include:
					grp=colsGroupMap[col0]
					if grp=="":
						outputFields.append(field)
					else:
						outputFields.append(prefix+grp+suffix)
		else:
			for col0,include,field in zip(colIndx,includes0,fields):
				if include:
					grp=colsGroupMap[col0]
					if grp=="":
						outputFields.append(field)
					else:
						try:
							thisMethod=groupMethodMap[grp]
						except:
							thisMethod=method #the default!
						
						outputFields.append(str(calculateGroupValue(fields,groupColsMap[grp],thisMethod)))
		
		print >> stdout,ofs.join(outputFields)			
	fin.close()
				

def printUsage(programName):
	print >> stderr,"Usage:",programName,"[options] filename"
	print >> stderr,"Options:"
	print >> stderr,"\t--unpairByNames. Do not pair samples by names"
	print >> stderr,"\t--prefixGroupNames,suffixGroupName  name.  Prefix or suffix to add for groups"
	print >> stderr,"\t--group colSelector=groupName+... "
	print >> stderr,"\t--method method specify the method to use. [mean], meanRO, median, medianRO, max, maxRO, min, minRO"
	print >> stderr,"\t--grpMethod groupName,method.  specify group specific method"
	print >> stderr,"\t--headerRow row. indicate row number of header. default =1"
	print >> stderr,"\t--fs,--ofs,--sep sepchar.  input, output, both separators, respectively"
			

if __name__=="__main__":
	optlist,args=getopt(sys.argv[1:],'',['ungroupByNames','prefixGroupNames=','suffixGroupNames=','group=','method=','grpMethod=','headerRow=',"fs=","ofs=","sep="])
	
	groupByNames=True

	if len(args)<1:
		printUsage(sys.argv[0])
		sys.exit()
	filename=args[0]

	groupMethodMap=dict()
	groupPrefix=dict()
	groupSuffix=dict()
	prefix=""
	suffix=""
	fs="\t"
	ofs="\t"
	method="mean"
	headerRow=1
	groupMapCommand=[]
	for opt,val in optlist:
		if opt=="--ungroupByNames":
			groupByNames=False
		elif opt=="--prefixGroupNames":
			prefix=val
		elif opt=="--suffixGroupNames":
			suffix=val
		elif opt=="--method":
			method=val
		elif opt=="--headerRow":
			headerRow=int(val)
		elif opt=="--sep":
			fs=replaceSpecialChar(val)
			ofs=fs
		elif opt=="--ofs":
			ofs=replaceSpecialChar(val)
		elif opt=="--fs":
			fs=replaceSpecialChar(val)
		elif opt=="--grpMethod":
			params.val.split(",")
			groupMethodMap[params[0]]=params[1]
		elif opt=="--group":
			blocks=val.split("+")
			for block in blocks:
				params=block.split("=")
				groupMapCommand.append(params)
	
	header,prestart=getHeader(filename,headerRow,headerRow,fs)
	
	colsGroupMap=[]
	
	for i in range(0,len(header)):
		colsGroupMap.append("")

	groupColsMap=dict()
	
		
	includes0=[]		
	
	

	if groupByNames:
		ancestralCol=dict()
		
		for col0,colName in zip(range(0,len(header)),header):
			if colName in ancestralCol:
				if not groupColsMap.has_key(colName):
					ancestor=ancestralCol[colName]
					groupColsMap[colName]=[ancestor,col0]
					colsGroupMap[ancestor]=colName
					colsGroupMap[col0]=colName
				else:
					groupColsMap[colName].append(col0)
					colsGroupMap[col0]=colName
					
			else:
				ancestralCol[colName]=col0
		
			

	for selector,groupName in groupMapCommand:
		cols0=sortu(getCol0ListFromCol1ListStringAdv(header,selector))
		
		for col0 in cols0:
			if colsGroupMap[col0]!="":
				print >> stderr,"col already got a group, abort!"
				sys.exit()

			colsGroupMap[col0]=groupName
		
		if groupColsMap.has_key(groupName):
			print >> stderr,"Duplicate Group Name, abort!"
			sys.exit()

		groupColsMap[groupName]=cols0

	for col0 in range(0,len(header)):
		grp=colsGroupMap[col0]
		if grp=="":
			includes0.append(True)
		elif groupColsMap[grp][0]==col0:
			includes0.append(True)
		else:
			includes0.append(False)


	
	collapseSamples_Main(filename,prefix,suffix,method,groupMethodMap,groupColsMap,colsGroupMap,includes0,fs,ofs)
		
			

	
