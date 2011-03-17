#!/usr/bin/env python

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

''' ATR
NODE1X  ARRY29X ARRY7X  0.515771470649
NODE2X  NODE1X  ARRY6X  0.467319235028
NODE3X  ARRY28X ARRY27X 0.443102402778
NODE4X  ARRY16X NODE2X  0.396103306443
NODE5X  ARRY13X ARRY1X  0.365913334462
NODE6X  ARRY24X ARRY20X 0.356523646025
NODE7X  ARRY18X ARRY4X  0.333905876029
NODE8X  ARRY21X ARRY15X 0.332370734808
NODE9X  NODE6X  NODE4X  0.327044321505
NODE10X ARRY17X NODE9X  0.28805077793

[clustering]>colStat.py -r1,2 RNASeqData_HJAY_matched_cgm_ng_pearson_average.cdt 
[:::::                  R 1                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       eventID
2                       B                       NAME
3                       C                       GWEIGHT
4                       D                       BT20_basal
5                       E                       HCC1143_basal
6                       F                       HCC3153_basal
7                       G                       184A1N4_basal
8                       H                       184B5_basal
9                       I                       MCF12A_basal
10                      J                       MCF10A_basal
11                      K                       HCC1954_basal
12                      L                       MCF10F_basal
13                      M                       HCC1500_basal
14                      N                       SUM185PE_luminal
15                      O                       HCC1187_basal
16                      P                       MDAMB231_claudinlow
17                      Q                       HBL100_claudinlow
18                      R                       HCC38_claudinlow
19                      S                       BT549_claudinlow
20                      T                       MDAMB157_claudinlow
21                      U                       MDAMB435_claudinlow
22                      V                       SUM159PT_claudinlow
23                      W                       600MPE_luminal
24                      X                       CAMA1_luminal
25                      Y                       BT474_luminal
26                      Z                       MDAMB361_luminal
27                      AA                      MDAMB415_luminal
28                      AB                      SKBR3_luminal
29                      AC                      MCF7_luminal
30                      AD                      MDAMB453_luminal
31                      AE                      SUM52PE_luminal
32                      AF                      T47D_luminal
33                      AG                      ZR751_luminal
34                      AH                      ZR75B_luminal
[:::::                  R 2                     :::::]
Index                   Excel                   Field
-----                   -----                   -----
1                       A                       AID
2                       B
3                       C
4                       D                       ARRY3X
5                       E                       ARRY8X
6                       F                       ARRY12X
7                       G                       ARRY0X
8                       H                       ARRY1X
9                       I                       ARRY13X
10                      J                       ARRY30X
11                      K                       ARRY11X
12                      L                       ARRY14X
13                      M                       ARRY10X
14                      N                       ARRY25X
15                      O                       ARRY9X
16                      P                       ARRY17X
17                      Q                       ARRY6X
18                      R                       ARRY7X
19                      S                       ARRY29X
20                      T                       ARRY16X
21                      U                       ARRY20X
22                      V                       ARRY24X
23                      W                       ARRY2X
24                      X                       ARRY5X
25                      Y                       ARRY4X
26                      Z                       ARRY18X
27                      AA                      ARRY19X
28                      AB                      ARRY22X
29                      AC                      ARRY15X
30                      AD                      ARRY21X
31                      AE                      ARRY23X
32                      AF                      ARRY26X
33                      AG                      ARRY27X
34                      AH                      ARRY28X


'''


def dfsGetList(adjList,visited,source):
	L=[]	
	if source in visited:
		return

	Q=[source]
	while len(Q)>0:
		u=Q.pop(0)
		if u in visited:
			continue
		visited.add(u)
		L.append(u)
		if u not in adjList:
			continue
		for v in adjList[u]:
			if v in visited:
				continue
			Q.append(v)

	return L
			

from sys import *
from getopt import getopt

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['out-top-correl='])
	
	outTopCorrel=""
	
	for o,v in opts:
		if o=='--out-top-correl':
			outTopCorrel=v
	
	try:
		cdtfile,atrfile=args
	except:
		print >> stderr,"Usage:",programName,"[options] cdtfile atrfile > group1 2> group2"
		print >> stderr,"--out-top-correl ofile. Output the top correlation into ofile"
		exit()

	
	ArrayMap=dict()
	#read in cdt file
	fil=open(cdtfile)
	lino=0
	for lin in fil:
		lino+=1
		fields=lin.rstrip("\r\n").split("\t")
		if lino==1:
			values=fields
			continue
		if lino==2:
			keys=fields
			for key,value in zip(keys,values):
				key=key.strip()
				value=value.strip()
				if len(key)==0 or len(value)==0:
					continue
				ArrayMap[key]=value

			break

	fil.close()

	InDeg=dict()
	ChildrenLists=dict()
	Correlations=dict()
	uparents=set()

	#read in atr file
	fil=open(atrfile)
	for lin in fil:
		fields=lin.rstrip().split("\t")
		if len(fields)<4:
			print >> stderr,"bad formatting of atr file",lin
			exit()
				
		parent,child1,child2=fields[:3]
		if parent in ChildrenLists:
			print >> stderr,"bad structure in atr file",parent,"is already a parent before",lin
			exit()
		
		if child1 in InDeg:
			print >> stderr,"bad structure in atr file",child1,"is already a child before",lin
			exit()
		
		if child2 in InDeg:
			print >> stderr,"bad structure in atr file",child2,"is already a child before",lin
			exit()

		InDeg[child1]=1
		InDeg[child2]=1
		try:
			uparents.remove(child1)
		except KeyError:
			pass
		try:
			uparents.remove(child2)
		except KeyError:
			pass
		ChildrenLists[parent]=[child1,child2]
		Correlations[parent]=float(fields[3])
		uparents.add(parent)
	
	fil.close()
			
	uparents=list(uparents)
	if len(uparents)!=1:
		print >> stderr,"bad structure in atr file: ultimate parent not a singleton",uparents
		exit()

	

	uparent=uparents[0]

	#print >> stderr,ChildrenLists
	#print >> stderr,ChildrenLists[uparent]
	#print >> stderr,Correlations[uparent]
	if outTopCorrel!="":
		fout=open(outTopCorrel,"w")
		print >> fout,Correlations[uparent]
		fout.close()
	
	visited=set()
	#now dfs in the left child of parent to stdout
	leftList=dfsGetList(ChildrenLists,visited,ChildrenLists[uparent][0])
	#print >> stderr, leftList
	for l in leftList:
		try:
			print >> stdout,ArrayMap[l]	
		except KeyError:
			pass

	#now dfs in the right child of parent to stderr
	rightList=dfsGetList(ChildrenLists,visited,ChildrenLists[uparent][1])	
	for l in rightList:
		try:
			print >> stderr,ArrayMap[l]		
		except KeyError:
			pass
	
