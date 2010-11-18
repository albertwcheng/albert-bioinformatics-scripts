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

from sys import *


def isInGroup(label,groupKeys):
	for groupKey in groupKeys:
		if groupKey in label:
			return True

	return False


def groupMembershipCount(labels,group1Keys,group2Keys):
	group1Count=0
	group2Count=0
	group1Items=[]
	group2Items=[]
	for label in labels:
		label=label.strip()
		inGroup1=isInGroup(label,group1Keys)
		inGroup2=isInGroup(label,group2Keys)
		if inGroup2 and inGroup1:
			print >> stderr,"error,label is not both groups"
			exit()
		if not inGroup2 and not inGroup1:
			print >> stderr,"error,label not in either group"
			exit()		
		if inGroup1:
			group1Count+=1
			group1Items.append(label)
		if inGroup2:
			group2Count+=1
			group2Items.append(label)

	return (group1Count,group1Items,group2Count,group2Items)

def getFileContent(filename):
	fil=open(filename)
	content=fil.readlines()
	fil.close()
	return content
		
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		group1file,group2file,groupIndicator1,groupIndicator2=args
	except:
		print >> stderr,programName,"group1file group2file groupIndicator1 [e.g., basal,claudinlow:invasive] groupIndicator2 [e.g., luminal:noninvasive]"
		exit()

	
	group1Keys,group1Name=groupIndicator1.split(":")
	group2Keys,group2Name=groupIndicator2.split(":")
	group1Keys=group1Keys.split(",")
	group2Keys=group2Keys.split(",")

	print >> stdout,"groupname[1]="+group1Name
	print >> stdout,"groupname[2]="+group2Name	


	#for groupfile1
	group1Count,group1Items,group2Count,group2Items=groupMembershipCount(getFileContent(group1file),group1Keys,group2Keys)
	print >> stdout,"groupfile1groupcount[1]="+str(group1Count)
	print >> stdout,"groupfile1groupcount[2]="+str(group2Count)
	print >> stdout,"groupfile1groupItems[1]="+",".join(group1Items)
	print >> stdout,"groupfile1groupItems[2]="+",".join(group2Items)
	totalItem=group1Count+group2Count

	if group1Count==0 or group2Count==0:
		outlier=0
		outlierIndex=-1
		outItems=[]
	elif group1Count==group2Count:
		#mixed!
		outlier=group1Count
		outlierIndex=0
		outItems=group1Items
	elif group1Count<group2Count:
		#group1 is outlier
		outlier=group1Count
		outlierIndex=1
		outItems=group1Items
	elif group2Count<group1Count:
		outlier=group2Count
		outlierIndex=2
		outItems=group2Items


	print >> stdout,"groupfile1outlierindex="+str(outlierIndex)
	print >> stdout,"groupfile1outlierNum="+str(outlier)
	print >> stdout,"groupfile1outlierItems="+",".join(outItems)
	print >> stdout,"groupfile1totalNum="+str(totalItem)

	grandTotalOutlier=outlier
	grandTotalItem=totalItem

	#for groupfile2
	group1Count,group1Items,group2Count,group2Items=groupMembershipCount(getFileContent(group2file),group1Keys,group2Keys)
	print >> stdout,"groupfile2groupcount[1]="+str(group1Count)
	print >> stdout,"groupfile2groupcount[2]="+str(group2Count)
	print >> stdout,"groupfile2groupItems[1]="+",".join(group1Items)
	print >> stdout,"groupfile2groupItems[2]="+",".join(group2Items)
	totalItem=group1Count+group2Count

	if group1Count==0 or group2Count==0:
		outlier=0
		outlierIndex=-1
		outItems=[]
	elif group1Count==group2Count:
		#mixed!
		outlier=group1Count
		outlierIndex=0
		outItems=group1Items
	elif group1Count<group2Count:
		#group1 is outlier
		outlier=group1Count
		outlierIndex=1
		outItems=group1Items
	elif group2Count<group1Count:
		outlier=group2Count
		outlierIndex=2
		outItems=group2Items


	print >> stdout,"groupfile2outlierindex="+str(outlierIndex)
	print >> stdout,"groupfile2outlierNum="+str(outlier)
	print >> stdout,"groupfile2outlierItems="+",".join(outItems)
	print >> stdout,"groupfile2totalNum="+str(totalItem)

	grandTotalOutlier+=outlier
	grandTotalItem+=totalItem	

	print >> stdout,"grandTotalOutlier="+str(grandTotalOutlier)
	print >> stdout,"grandTotalItem="+str(grandTotalItem)
	
	
