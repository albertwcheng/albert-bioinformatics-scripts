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

def properpvalue(pvalues):
	n=0
	for p in pvalues:
		if p>=0 and p<=1:
			n+=1
	
	return n		

def pvalues2FDRInPlace(pvalues,FDRError=2): #give back an pvalue -> FDR map
	pvalues.sort()
	totalNum=len(pvalues)
	properTotal=properpvalue(pvalues)
	pvi=0
	ppv=-100
	pvalues2FDRMap=dict()

	while pvi<totalNum:
		while ppv==pvalues[pvi]:
			pvi+=1
			if pvi==totalNum:
				break
			
		#now pvi is the number of pvalues<= previous pvalue
		
		if pvi>=1:
			if ppv>=0 and ppv<=1:
				FDR=min([float(properTotal)*ppv/pvi,1.0])
				
			else:
				FDR=FDRError	

			pvalues2FDRMap[ppv]=FDR	
		
		if pvi==totalNum:
			break		
		ppv=pvalues[pvi]

	return pvalues2FDRMap

def getFDRsForPvaluesNotInPlace(pvalues):
	pvalueIP=pvalues[:]
	pvalueFDRMap=pvalues2FDRInPlace(pvalueIP)
	
	FDR=[]
	
	for pvalue in pvalues:
		FDR.append(pvalueFDRMap[pvalue])

	return FDR
		
