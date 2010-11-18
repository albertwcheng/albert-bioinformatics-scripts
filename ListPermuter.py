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


import sys
#give L the data list, other as empty lists
def nextPermutationOfList(L,permuterGraph,Queue,levelAdditor):
	levels=len(L)
	
	additor=1
	
	if levels==0:
		return []
	if len(permuterGraph)==0:
		#initialize it and put all nodes into queue
		for i in range(0,len(L)):
			permuterGraph.append([0,0])
			Queue.append([i,[L[i]]]) #the node id and a list of one-element corresponding to the ith element of L	
			if i<2:
				levelAdditor.append(1)
			else:
				additor*=i
				levelAdditor.append(additor)
	
		levelAdditor.reverse()
		levelAdditor.insert(0,0)

	
	if len(Queue)==0:
		#end of all permutations.
		return []		
	#DFS until reaching the list length
	
	levelAdditor[0]+=1 #next thread
	curThread=levelAdditor[0]
	
	while(len(Queue)>0):
		u,curL=Queue.pop(0)
		thisLevel=len(curL)
		permuterGraph[u][1]=curThread+levelAdditor[thisLevel]
		
		if thisLevel==levels:
			return curL
		
		
		for i in range(0,levels):
			if permuterGraph[i][1]<=curThread:
				#can go
				Queue.insert(0,[i,curL+[L[i]]])


def nextPermutationOfString(L,permuterGraph,Queue,levelAdditor):
	levels=len(L)
	
	additor=1
	
	if levels==0:
		return []
	if len(permuterGraph)==0:
		#initialize it and put all nodes into queue
		for i in range(0,len(L)):
			permuterGraph.append([0,0])
			Queue.append([i,L[i]]) #the node id and a list of one-element corresponding to the ith element of L	
			if i<2:
				levelAdditor.append(1)
			else:
				additor*=i
				levelAdditor.append(additor)
	
		levelAdditor.reverse()
		levelAdditor.insert(0,0)

	
	if len(Queue)==0:
		#end of all permutations.
		return []		
	#DFS until reaching the list length
	
	levelAdditor[0]+=1 #next thread
	curThread=levelAdditor[0]
	
	while(len(Queue)>0):
		u,curL=Queue.pop(0)
		thisLevel=len(curL)
		permuterGraph[u][1]=curThread+levelAdditor[thisLevel]
		
		if thisLevel==levels:
			return curL
		
		
		for i in range(0,levels):
			if permuterGraph[i][1]<=curThread:
				#can go
				Queue.insert(0,[i,curL+L[i]])



def getAllPermutationOfString(S):
	permuterGraph=[]
	Queue=[]
	levelAdditor=[]
	allStrings=[]
	while(True):
		perm=nextPermutationOfString(S,permuterGraph,Queue,levelAdditor)
		if len(perm)==0:
			return allStrings
		
		allStrings.append(perm)	

def getAllPermutationOfList(L):
	permuterGraph=[]
	Queue=[]
	levelAdditor=[]
	allLists=[]
	while(True):
		perm=nextPermutationOfList(L,permuterGraph,Queue,levelAdditor)
		if len(perm)==0:
			return allLists
		
		allLists.append(perm)		


if __name__=="__main__":
	a_str=sys.argv[1]
	permuterGraph=[]
	Queue=[]
	levelAdditor=[]
	while(True):
		perm=nextPermutationOfString(a_str,permuterGraph,Queue,levelAdditor)
		if len(perm)==0:
			break
		print perm
		
