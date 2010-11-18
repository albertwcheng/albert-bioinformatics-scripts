
'''
albertcommon.py
A module containing all the common functions for the scripts 


 
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


from math import floor
import sys
import types
import re
import os

def generic_istream(filename):
	#print >> stderr,"opening ",filename
	if filename=="-":
		return sys.stdin
	else:
		return open(filename)

def medianOfSortedList(L):
	lList=len(L)
	if lList%2==0:
		return (L[lList/2-1]+L[lList/2])/2.0
	else:
		return L[lList/2]

def sortedList(L):
	LC=L[:]
	LC.sort()
	return LC	

def multiplyVector(L,by):
	LC=[]
	for x in L:
		LC.append(x*by)
	
	return LC

def vectorComparator(v1,v2):
	try:
		for v1v,v2v in zip(v1,v2):
			if v1v<v2v:
				return -1
			elif v1v>v2v:
				return 1
				

	except IndexError:
		if len(v1v)<len(v2v):
			return -1
		elif len(v1v)>len(v2v):
			return 1
		else:
			#strange
			print >> sys.stderr,"strange",v1,v2
			return 0

	return 0



def SecondFieldComparator(x,y):
	if x[1]<y[1]:
		return -1
	elif x[1]>y[1]:
		return 1
	else:
		return 0

def ToIndexedTuples(L):
	IT=[]
	for i in range(0,len(L)):
		IT.append([i,L[i]])

	return IT

def rank(L,tieDivide):
	RANK=L[:]
	IT=ToIndexedTuples(L)
	IT.sort(SecondFieldComparator)
	#print >> sys.stderr,"IT is",IT
	if tieDivide:
		crank=0
		divider=1
		startI=0
		for curI in range(0,len(IT)+1):

			if curI!=len(IT):
				it=IT[curI]
				curValue=it[1]

			if curI==0:
				#startI=curI
				#divider=1
				prev=curValue
				continue #nothing else to do
				
			if prev!=curValue or curI==len(IT):
				if divider>1:
					thisRank=float(2*(crank+1)+divider-1)/2
				else:
					thisRank=crank+1
					
				for setI in range(startI,curI):
					RANK[IT[setI][0]]=thisRank
				
				if curI==len(IT):
					break

				crank+=divider
				startI=curI
				divider=1
				
				prev=curValue
			else:
				divider+=1
		
		
					
	else:
		for i,it in zip(range(0,len(IT)),IT):
			origindex,value=it
			RANK[origindex]=i+1
	
	return RANK


def StrListToFloatList(L):
	LC=[]
	for s in L:
		LC.append(float(s))
	return LC

def toStrList(L):
	LC=[]
	for i in L:
		LC.append(str(i))
	return LC


def medianOfList(L):

	return medianOfSortedList(sortedList(L))

def selectListByIndexVector(L,I):
		
	newL=[]
	try:	
		for i in I:
			newL.append(L[i])
		return newL
	except:
		return []

def percentileOfList(p,L):
	LSorted=L[:]
	LSorted.sort()	
	l=len(LSorted)
	i=int(round(float(l-1)*p))
	return LSorted[i]

def countIfInRangeInc(low,hi,L):
	c=0	
	for x in L:
		if low<=x and x<=hi:
			c+=1
	return c

def countIf(needles,L):
	c=0
	for x in L:
		if x in needles:
			c+=1
	return c	

def divMod(num,div):
	k=int(num)/int(div)
	d=int(num)%int(div)
	return k,d

def dissociatekd(n):
	k=floor(n)
	d=n-k
	return k,d

def percentilesOfSortedList(L,precentiles):
	N=len(L)
	RESULT=[]
	for percentile in precentiles:
		n=float(percentile)/100*(N-1)+1
		k,d=dissociatekd(n)
		if k==1:
			val=L[0]
		elif k==N:
			val=L[N-1]
		else:
			val=L[int(k-1)]+d*(L[int(k)]-L[int(k-1)])		
		
		RESULT.append(val)
	
	return RESULT

def percentilesOfList(L,percentiles):
	return percentilesOfSortedList(sortedList(L),percentiles)


def outlierBounds(L):
	LQ,UQ=percentilesOfList(L,[25,75])
	IQ=UQ-LQ
	return LQ-1.5*IQ,UQ+1.5*IQ


def rangeListFromRangeString(rangestring,transform):
	rangeValues=[]
	rangestring=rangestring.strip()
	if rangestring=='0' or rangestring=='-' or rangestring=="":
		return rangeValues #mod 3/31/2009

	col1splits=rangestring.split(",")
	for col1split in col1splits:
		col1rangesplit=col1split.split("-")
		if len(col1rangesplit)==1:
			rangeValues.append(int(col1rangesplit[0])+transform)
		else:
			try:
				for coltoAdd in range(int(col1rangesplit[0])+transform,int(col1rangesplit[1])+1+transform):
					rangeValues.append(coltoAdd)
			except ValueError:
				pass	
			
	return rangeValues	


def multiColJoinField(headerFields,val):
	#print >> sys.stderr, val
	
	
	splitons=val.split("%")

	#print >> sys.stderr,splitons
	filename=splitons[0]
	
	if len(splitons)>1:
		sep=replaceSpecialChar(splitons[1])
	else:
		sep="\t"
	
	istream= generic_istream(filename)
	
	fieldsToInclude=[]

	for line in istream:
		line=line.strip("\r\n")
		fieldsToInclude.extend(line.split(sep))
	
	indices=dict()	
	
	indRange=range(0,len(headerFields))
	for i,headerF in zip(indRange,headerFields):				
		if headerF in fieldsToInclude:
			if not indices.has_key(headerF):
				indices[headerF]=[i]
			else:
				indices[headerF].append(i)

	istream.close()
	
	#print >> sys.stderr,indices
	indicesOut=[]

	for fieldToInclude in fieldsToInclude:
		try:
			indicesOut.extend(indices[fieldToInclude])
		except KeyError:
			pass
	#print >> sys.stderr,indicesOut
	return indicesOut

def rangeListFromRangeStringAdv(headerFields,rangestring,transform):
	rangeValues=[]
	rangestring=rangestring.strip()
	if rangestring=='0' or rangestring=='-' or rangestring=="":
		return rangeValues #mod 3/31/2009
	


	
	sortMode=0 #0:no sort, 1: ascending, -1: descending
	
	col1splits=rangestring.split(",")
	for curColSplitI in range(0,len(col1splits)):
		col1split=col1splits[curColSplitI]
		col1rangesplit=col1split.split("-")
		
		for i in range(0,len(col1rangesplit)):
			#print col1rangesplit[i],
			col1rangesplit[i]=replaceSpecialChar(col1rangesplit[i])
			#print col1rangesplit[i]

		if len(col1rangesplit)==1:
			director=col1rangesplit[0][0]
			if director in [".","@","%"]: #it's a header string!
				if director=='.':
					indices=multiColIndicesFromHeaderMerged(headerFields,[col1rangesplit[0][1:]])
				elif director=="%":
					indices=multiColJoinField(headerFields,col1rangesplit[0][1:])				
				else:
					p=re.compile(col1rangesplit[0][1:])
					indices=multiColIndicesFromHeaderMerged(headerFields,[p])
				if(len(indices)==0):
					print >> sys.stderr,"Error:",col1rangesplit[0][1:],"not found/matched in header"	
					sys.exit()
			
				for inx in indices:
					rangeValues.append(inx+1+transform)
				
			elif director=='_':
				rangeValues.append(len(headerFields)-int(col1rangesplit[0][1:])+1+transform)
			elif director=='a':
				sortMode=1
			elif director=='d':
				sortMode=-1
			elif director=='+':
				rangeValues.extend(range(0,len(headerFields)))
			elif director=='x':
				#added 7/15/2010 for excel styled column id
				rangeValues.append(excelIndxToCol0(col1rangesplit[0][1:])+1+transform) #converted back to 1-based and then do transform
			else:
				rangeValues.append(int(col1rangesplit[0])+transform)
		else: # x-x a range!
			try:
				#handle the left value of the bound
				if col1rangesplit[0][0]=='.':
					#print >> sys.stderr, headerFields
					indices=multiColIndicesFromHeaderMerged(headerFields,[col1rangesplit[0][1:]])
					if(len(indices)==0):
						print >> sys.stderr,"Error:",col1rangesplit[0][1:],"not found in header"	
						sys.exit()
					rangeL=min(indices)+1+transform
				elif col1rangesplit[0][0]=='@': #added 12/10/2009
					p=re.compile(col1rangesplit[0][1:])
					indices=multiColIndicesFromHeaderMerged(headerFields,[p])
					if(len(indices)==0):
						print >> sys.stderr,"Error:",col1rangesplit[0][1:],"not matched in header"	
						sys.exit()	
					rangeL=min(indices)
				elif col1rangesplit[0][0]=='_': #from the back added 12/10/2009
					rangeL=len(headerFields)-int(col1rangesplit[0][1:])+1+transform
				elif col1rangesplit[0][0]=='x':
					#added 7/15/2010 for excel styled column id
					rangeL=excelIndxToCol0(col1rangesplit[0][1:])+1+transform #converted back to 1-based and then do transform
				else:
					rangeL=int(col1rangesplit[0])+transform

				#handle the right value of the bound
				if col1rangesplit[1][0]=='.':
					indices=multiColIndicesFromHeaderMerged(headerFields,[col1rangesplit[1][1:]])
					if(len(indices)==0):
						print >> sys.stderr,"Error:",col1rangesplit[1][1:],"not found in header"	
						sys.exit()
					rangeH=max(indices)+2+transform
				elif col1rangesplit[1][0]=='@':
					p=re.compile(col1rangesplit[1][1:])
					indices=multiColIndicesFromHeaderMerged(headerFields,[p])
					if(len(indices)==0):
						print >> sys.stderr,"Error:",col1rangesplit[1][1:],"not matched in header"	
						sys.exit()						
					rangeH=max(indices)+2+transform
				elif col1rangesplit[1][0]=='_': #from the back added 12/10/2009
					rangeH=len(headerFields)-int(col1rangesplit[1][1:])+2+transform
				elif col1rangesplit[1][0]=='x':
					#added 7/15/2010 for excel styled column id
					rangeH=excelIndxToCol0(col1rangesplit[1][1:])+2+transform #converted back to 1-based and then do transform
				else:
					rangeH=int(col1rangesplit[1])+1+transform
				
				
				if rangeL>=rangeH:
					step=-1
					rangeH-=2
				else:
					step=1
				#print >> sys.stderr,rangeL,rangeH,step
				for coltoAdd in range(rangeL,rangeH,step):
					rangeValues.append(coltoAdd)
			
			except ValueError:
				pass	
	
	if sortMode==1:
		rangeValues.sort()
	elif sortMode==-1:
		rangeValues.sort()
		rangeValues.reverse()

	return rangeValues


def meanOfList(L):
	#print L
	return float(sum(L))/len(L)
	

def removeOutliers(L):
	if len(L)<3:
		return
	LB,UB=outlierBounds(L)
	for i in range(len(L)-1,-1,-1):
		if L[i]>UB or L[i]<LB:
			del L[i]


def getCol0ListFromCol1ListString(col1ValueString):
	
	return rangeListFromRangeString(col1ValueString,-1)

def getCol0ListFromCol1ListStringAdv(headerFields,col1ValueString):
	
	return rangeListFromRangeStringAdv(headerFields,col1ValueString,-1)

def sortu(L):
	return uniq(sortedList(L))

def uniq(L):
	LKey=[]
	UL=[]
	for l in L:
		if l not in LKey:		
			LKey.append(l)
			UL.append(l)

	return UL

MAX_INT=sys.maxint
MIN_INT=-MAX_INT-1


specialCharMap={ "\\t":"\t",
		 "\\n":"\n",
		 "\\r":"\r",
		 "^t":"\t",
		 "^b":" ",
		"^s":"<",
		"^g":">",
		"^c":",",
		"^d":".",
		"^^":"^",
		"^M":"$",
		"^m":"-",
		"^o":":",
		"^S":"\\"

		}




def replaceSpecialChar(S):
	for k,v in specialCharMap.items():
		#print >> sys.stderr, k#+"<"+S,
		S=S.replace(k,v)
	#print >> sys.stderr, S
	return S	

def mapSpecialChar(c,default):
	try:
		return specialCharMap[c]
	except KeyError:
		return default

def colIndicesFromHeader(headerFields,selectors):
	colIndices0=[]
	for selector in selectors:
		try:
			colIndices.append(headerFields.index(selector))
		except ValueError: #not found!
			colIndices.append(-1)

	return colIndices0

def indexAll(L,x):
	indices=[]
	start=0
	if type(x) is types.StringType:
		for i in range(0,len(L)):
			if x==L[i]:
				indices.append(i)
		
	else: # assume regex
		for i in range(0,len(L)):
			if x.search(L[i]) is not None:
				indices.append(i)
	

	return indices	

def multiColIndicesFromHeaderWithSelector(headerFields,selectors):
	colIndices0=[]
	for selector in selectors:
		colIndices0.append([selector,indexAll(headerFields,selector)])

	return colIndices0
	
def multiColIndicesFromHeaderMerged(headerFields,selectors):
	colIndices0=[]
	for selector in selectors:
		colIndices0.extend(indexAll(headerFields,selector))

	return colIndices0

def getHeader(filename,headerRow,startRow,FS):
	try:
		fil=generic_istream(filename)
	except IOError:
		print >> sys.stderr,"Cannot open",filename
		return
	
	header=[]
	prestartRows=[]
	c=0;
	for lin in fil:
		c+=1;
		if(c==headerRow):
			lin=lin.rstrip()
			if FS=="":
				header=lin.split()
			else:
				header=lin.split(FS)
		
		if(c<startRow):
			lin=lin.rstrip()
			if FS=="":
				prestartRows.append(lin.split())
			else:
				prestartRows.append(lin.split(FS))		
	

	fil.close()	

	return header,prestartRows

def explainColumns(stream):
	print >> stream,"cols format:"
	print >> stream,"\t* inserts all columns"
	print >> stream,"\tnumber: 1-5,3"
	print >> stream,"\tnumber preceded by '_' means from the end. _1 means last row, _2 second last"
	print >> stream,"\tfield name preceded by '.': .exp-5,.pvalue-.fdr"
	print >> stream,"\texcel column preceded by 'x': xB-xAA means column 2 to column 27"
	print >> stream,"\tregex preceded by '@': @FDR[a-z]"
	print >> stream,"\t%filename%sep or just %filename: open file which contains the fields to include. default separator is [TAB]"
	print >> stream,"\tif last field is a. Then following columns are added as ascending. If appears at end, all are sorted ascending"
	print >> stream,"\tis last field is d. Then following columns are added as descending. If appears at end, all are sorted descending"

def getSubvector(D,I,sortIndex=False):
	subv=[]
	nI=I	
	if sortIndex:	
		nI=I[:]
		nI.sort()

	for i in nI:
		subv.append(D[i])

	return subv	


def getSubVectorByBinarySelector(D,I):
	subv=[]
	for i,d in zip(I,D):
		if i:
			subv.append(d)

	return subv

def toStrVector(V):
	sV=[]
	for v in V:
		sV.append(str(v))
	return sV

def excelColIndex(idx0):
	k,d=divMod(idx0,26)
	D=[d]
	while k>=1:
		k,d=divMod(k-1,26)
		D.append(d)
	outString=""
	for d in D:
		outString=chr(ord('A')+(d))+outString

	return outString

def excelIndxToCol0(alphaString):
	idx=0
	multiplier=1
	for i in range(len(alphaString)-1,-1,-1):
		idx+=(ord(alphaString[i])-ord('A')+1)*multiplier
		multiplier*=26

	return idx-1

def testExcelString():
	for idx0 in range(0,20000):
		print >> stderr,(idx0+1),
		excelString=excelColIndex(idx0)
		print >> stderr,"excel="+excelString,
		rcol0=excelIndxToCol0(excelString)
		print >> stderr,"reverted="+str(rcol0+1)
		if rcol0!=idx0:
			print >> stderr,"error"
			exit()

def basename(filename):
	return os.path.basename(filename)

def cleanfilename(filename):
	bn=basename(filename)
	bn=bn.split(".")
	if len(bn)>1:
		del bn[-1]
	
	return ".".join(bn)

#from [ [1,2,3],[1],[1,2] ] => [ [1,1,1],[1,1,2],[2,1,1],[2,1,2],[3,1,1],[3,1,2] ]
def findAllCombinations(ListOfLists):
	numberOfPositions=len(ListOfLists)
	numberOfCombinations=1
	bounds=[]
	current=[]	
	for L in ListOfLists:
		numInList=len(L)
		numberOfCombinations*=numInList
		bounds.append(numInList)
		current.append(0)

	combinations=[]
	current[-1]=-1


	for cI in range(0,numberOfCombinations):
		thisCombination=[]
		#thisIndex=[]
		combinations.append(thisCombination)
		OK=False
		indexI=numberOfPositions-1
		while not OK:
			if current[indexI]==bounds[indexI]-1:
				#reset this and keep status to not OK
				current[indexI]=0		
			else:
				current[indexI]+=1
				OK=True
			#push current element to front
			#print >> stderr,current
			thisCombination.insert(0,ListOfLists[indexI][current[indexI]])
			#thisIndex.insert(0,current[indexI])
			indexI-=1

		while indexI>=0:
			thisCombination.insert(0,ListOfLists[indexI][current[indexI]])
			indexI-=1

		#print >> thisIndex

	return combinations

def debugFindAllCombinations():
	print >> stderr, findAllCombinations([ [1,2,3],[1],[1,2] ])
	print >> stderr, findAllCombinations([ ['amy','fiona','kate'],['likes','hates','kisses'],['jason','albert'] ])
	exit()


if __name__=='__main__':
	L=[1,2,3,5,4,6,7]
	print percentilesOfList(L,[25,75])
	print outlierBounds(L)

