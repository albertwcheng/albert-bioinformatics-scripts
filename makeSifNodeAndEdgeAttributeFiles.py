#!/usr/bin/env python

'''

makeSifNodeAndEdgeAttributeFiles.py

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

from optparse import OptionParser
from sys import *
from albertcommon import *

def printUsageAndExit(parser):
	parser.print_help(stderr)
	explainColumns(stderr)
	exit()

def getSortedNodeInteractionTuple(node1,interactionType,node2):
	return (min(node1,node2),interactionType,max(node1,node2))

if __name__=='__main__':
	programName=argv[0]
	
	usage="usage: %prog [options] filename node1IDCol node2IDCol"+\
	"""

Make SIF, node attribute and edge attribute files for use by Cytoscape
(c) Albert W Cheng 2010
	"""

	parser=OptionParser(usage,add_help_option=False)
	parser.add_option("-h","--help",dest="help",default=False,action="store_true",help="show this help message and exit")
	parser.add_option("--node-attribute",dest="node_attribute",action="append",nargs=4,default=None,help="create node attribute file to the specified filename. 4 arguments required: filename attributeName value1Col[.:ignore] value2Col[.:ignore]")
	parser.add_option("--sif",dest="sif",default=None,help="create SIF network file to the specified filename")
	parser.add_option("--edge-attribute",dest="edge_attribute",action="append",nargs=3,default=None,help="create edge attribute file to the specified filename. 3 arguments required: filename attributeName valueCol")
	parser.add_option("--interaction-type",dest="interaction_type",default=None,help="set interaction type to a constant. Default is interacts_with")
	parser.add_option("--interaction-type-col",dest="interaction_type_col",default=None,help="retrive interaction type from a col. Default is the constant interaction type interacts_with")
	parser.add_option("--header-row",default=1,dest="headerRow",type="int",help="set header row. Default is 1")
	parser.add_option("--start-row",default=2,dest="startRow",type="int",help="set start row. Default is 2")
	parser.add_option("--fs",default="\t",dest="fs",help="set field separator. Default is tab")
	parser.add_option("--ofs",default=" ",dest="ofs",help="set output field separator. Default is space")
	parser.add_option("--undirected",dest="undirected",default=False,action="store_true",help="output an undirected graph. unique on (node1,node2,interaction)")
	parser.add_option("--avoid-edge-attr-values",dest="avoidEdgeAttrValues",action="append",default=None,help="set edge attribute values that are invalid and are ignored from being put into attribute file")
	parser.add_option("--avoid-node-attr-values",dest="avoidNodeAttrValues",action="append",default=None,help="set node attribute values that are invalid and are ignored from being put into attribute file")
	
	(options,args)=parser.parse_args()

	try:
		filename,node1IDCol,node2IDCol=args
	except:
		printUsageAndExit(parser)

	fs=replaceSpecialChar(options.fs)

	header,prestarts=getHeader(filename,options.headerRow,options.startRow,fs)
	node1IDCol=getCol0ListFromCol1ListStringAdv(header,node1IDCol)[0]
	node2IDCol=getCol0ListFromCol1ListStringAdv(header,node2IDCol)[0]

	Node_Attribute_Tasks=[]
	Edge_Attribute_Tasks=[]



	fileHandlesToClose=[]


	if options.sif:
		sifFilename=options.sif
		sifFile=open(sifFilename,"w")
		fileHandlesToClose.append(sifFile)
	else:
		sifFilename=""

	if options.node_attribute:
		for outf,attrName,value1Col,value2Col in options.node_attribute:
			if value1Col==".":
				value1Col=-1
			else:
				value1Col=getCol0ListFromCol1ListStringAdv(header,value1Col)[0]
			if value2Col==".":
				value2Col=-1
			else:
				value2Col=getCol0ListFromCol1ListStringAdv(header,value2Col)[0]
			
			outf=open(outf,"w")
			print >> outf,attrName
			fileHandlesToClose.append(outf)
			Node_Attribute_Tasks.append([outf,attrName,value1Col,value2Col,set()])

	if options.edge_attribute:
		for outf,attrName,valueCol in options.edge_attribute:
			valueCol=getCol0ListFromCol1ListStringAdv(header,valueCol)[0]

			outf=open(outf,"w")
			print >> outf,attrName
			fileHandlesToClose.append(outf)			
			Edge_Attribute_Tasks.append([outf,attrName,valueCol,set()])

	interactionTypeCol=-1
	interactionType="interacts_with"	

	if options.interaction_type and interaction_type_col:
		print >> stderr,"Both Interaction Type and Interaction Type Col Defined. These two are mutually exclusive and can only define one of them. Abort"
		printUsageAndExit(parser)

	if options.interaction_type:
		interactionType=options.interaction_type

	if options.interaction_type_col:
		interactionTypeCol=getCol0ListFromCol1ListStringAdv(header,interactionTypeCol)[0]
		
		
	if options.undirected:
		UndirectedNodeInteractionSet=set()

	fil=open(filename)

	lino=0
	for lin in fil:
		lino+=1		
		if lino<options.startRow:
			continue
		lin=lin.rstrip("\r\n")
		fields=lin.split(fs)		
		try:
			node1ID=fields[node1IDCol]

		except:
			node1ID=None
		try:
			node2ID=fields[node2IDCol]
		except:
			node2ID=None

		

		if options.interaction_type_col:
			try:
				interactionType=fields[interactionTypeCol]
			except:
				interactionType=None

		if node1ID and node2ID and interactionType:
			sortedInteractionTuple=getSortedNodeInteractionTuple(node1ID,interactionType,node2ID)
			if options.undirected:
				edgeName=options.ofs.join([sortedInteractionTuple[0],"("+sortedInteractionTuple[1]+")",sortedInteractionTuple[2]])
			else:
				edgeName=options.ofs.join([node1ID,"("+interactionType+")",node2ID])
		
		if options.sif: #output SIF
			if node1ID and node2ID and interactionType: #both ID and interaction type are valid
				if options.undirected:
					if sortedInteractionTuple not in UndirectedNodeInteractionSet:
						UndirectedNodeInteractionSet.add(sortedInteractionTuple)
						print >> sifFile,options.ofs.join(sortedInteractionTuple)
				else:	
					print >> sifFile,options.ofs.join([node1ID,interactionType,node2ID])

		for outf,attrName,value1Col,value2Col,nodeNameSet in Node_Attribute_Tasks:
			#if node1ID=="TNK2" or node2ID=="TNK2":
			#	print >> stderr,"found TNK2",attrName,node1ID,node2ID,value1Col,value2Col,nodeNameSet

			if value1Col!=-1 and node1ID:
				try:
					value1=fields[value1Col]

					if options.avoidNodeAttrValues and value1 in options.avoidNodeAttrValues:
						raise ValueError

					#if node1ID=='TNK2':
					#	print >> stderr,outf,attrName,value1Col,value2Col,nodeNameSet

					if node1ID in nodeNameSet:
						raise ValueError

					nodeNameSet.add(node1ID)

					
					print >> outf,options.ofs.join([node1ID,"=",value1])
				except:
					pass

			if value2Col!=-1 and node2ID:
				try:
					value2=fields[value2Col]

					if options.avoidNodeAttrValues and value2 in options.avoidNodeAttrValues:
						raise ValueError

					#if node2ID=='TNK2':
					#	print >> stderr,outf,attrName,value1Col,value2Col,nodeNameSet

					if node2ID in nodeNameSet:
						raise ValueError
					
					nodeNameSet.add(node2ID)

					
					print >> outf,options.ofs.join([node2ID,"=",value2])
				except:
					pass

		for outf,attrName,valueCol,edgeNameSet in Edge_Attribute_Tasks:
			if node1ID and node2ID and interactionType:
				try:
					value=fields[valueCol]
					
					if options.avoidEdgeAttrValues and value in options.avoidEdgeAttrValues:
						raise ValueError

					if edgeName in edgeNameSet:
						raise ValueError

					edgeNameSet.add(edgeName)
								

					print >> outf,options.ofs.join([edgeName,"=",value])
				except:
					pass


	#close all files

	fil.close()

	for fh in fileHandlesToClose:
		fh.close()

	
