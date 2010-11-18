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

import sys
from getopt import getopt
from sys import stdout,stderr,exit

#0007468 = regulation of rhodopsin gene expression  [isa	0010468 ] [partof 0046531 0042461 ]

def removeslash(str):
	return str.replace("\\","")



def __output(stream,IDs,name,is_a,part_of,other):
	for termID in IDs:
		outStr=termID+" = "+name+" "  #need a two space
		if len(is_a)>0:
			outStr+=" [isa: "+" ".join(is_a)+" ]"
		if len(part_of)>0:
			outStr+=" [partof: "+" ".join(part_of)+" ]"
		if len(other)>0:
			outStr+=" [other: "+" ".join(other)+" ]"

		print >> stream, outStr





def getNamespaceListFromOBO1_2File(filename):
	domain=""
	fil=open(filename)

	is_a=set()
	part_of=set()
	other=set()
	name=""
	IDs=set()
	
	curFiler=False
	

	for lin in fil:
		lin=lin.strip()
		if len(lin)==0: #skip empty lines
			continue		
		
		if lin[0]=="[": #new domain, new term?
			
			if len(name)>0:
				#__output(stdout,IDs,name,is_a,part_of,other)
				for _id in IDs:
					print >> stdout,"%s:%s\t%s" %(_id,name,namespace)			
				
			is_a=set()
			part_of=set()
			other=set()
			name=""
			IDs=set()
			namespace=""

			if lin[0:6]=="[Term]": #new term
				domain="Term"
				#clear term struct
			else:
				domain=""

			continue
			
			
		if len(domain)==0: #skip openings
			continue 
		
		if domain=="Term":
			firstColon=lin.index(":")
			key=lin[0:firstColon]
			value=lin[firstColon+2:]
			if key in ["id","alt_id"]:
				IDs.add(value[3:])
			elif key=="name":
				name=value
			elif key=="namespace":
				namespace=value
			elif key=="is_a":
				value_split=value.split(" ")
				is_a.add(value_split[0][3:])
			elif key=="relationship":
				value_split=value.split(" ")
				if value_split[0]=="part_of":
					part_of.add(value_split[1][3:])
				else:
					other.add(value_split[1][3:])
		


	fil.close()

	if len(name)>0:
		for _id in IDs:
			print >> stdout,"%s:%s\t%s" %(_id,name,namespace)			

def convertGeneOntologyOrgOBO1_2FileToBinGO(filename):
	domain=""
	fil=open(filename)

	is_a=set()
	part_of=set()
	other=set()
	name=""
	IDs=set()
		

	for lin in fil:
		lin=lin.strip()
		if len(lin)==0: #skip empty lines
			continue		
		
		if lin[0]=="[": #new domain, new term?
			
			if len(name)>0:
				__output(stdout,IDs,name,is_a,part_of,other)				
				
			is_a=set()
			part_of=set()
			other=set()
			name=""
			IDs=set()

			if lin[0:6]=="[Term]": #new term
				domain="Term"
				#clear term struct
			else:
				domain=""

			continue
			
			
		if len(domain)==0: #skip openings
			continue 
		
		if domain=="Term":
			firstColon=lin.index(":")
			key=lin[0:firstColon]
			value=lin[firstColon+2:]
			if key in ["id","alt_id"]:
				IDs.add(value[3:])
			elif key=="name":
				name=value
			elif key=="is_a":
				value_split=value.split(" ")
				is_a.add(value_split[0][3:])
			elif key=="relationship":
				value_split=value.split(" ")
				if value_split[0]=="part_of":
					part_of.add(value_split[1][3:])
				else:
					other.add(value_split[1][3:])
		


	fil.close()

	if len(name)>0:
		__output(stdout,IDs,name,is_a,part_of,other)

def convertGeneOntologyOrgToBinGOGO(filename):
	terms=dict()  #terms[id]=[name,is_a(set),part_of(set),other(set)]	
	fil=open(filename)

	parent=dict() #parent[ident]=[id,...]

	prevIdent=0;
	lino=0
	for lin in fil:
		lino+=1		
		lin=lin.rstrip()		
		if lin[0]=="!":
			#coment line contine
			continue

		oldlin=lin
		lin=lin.lstrip()
		thisIdent=len(oldlin)-len(lin)
		if (thisIdent-prevIdent) > 1:
			print >> stderr,lino,"ident error abort",thisIdent,prevIdent
			exit()
		
		relationship=lin[0]
		otherstuff=lin[1:]
		otherstuff_split=otherstuff.split(";")
		termName=removeslash(otherstuff_split[0].strip())
		GOs=otherstuff_split[1].replace("\,","").split(",")

		termStruct=[]

		for i in range(0,len(GOs)):
			GOs[i]=GOs[i][0:12].strip()
			GOs[i]=GOs[i][3:]
			if len(GOs[i])!=7:
				print >> stderr,lino,"GOTermIDformating error",GOs[i],lin
				exit()
			try:
				termStruct=terms[GOs[i]]
			except:
				pass

		#if termStruct is not set => new term

		if len(termStruct)==0:
			#new term
			name=termName
			is_a=set()
			part_of=set()
			other=set()
			
			termStruct=[name,is_a,part_of,other]
			for GO in GOs:
				terms[GO]=termStruct

		else:
			name,is_a,part_of,other=termStruct

		#now add relationship
		if thisIdent>0:
			thisParent=parent[thisIdent-1] #thisParent is now a list of terms


			if relationship=="<":
				targetSet=part_of
			elif relationship=="%":
				targetSet=is_a
			elif relationship in ["^","+","-","&"]:
				targetSet=other
			else:
				print >> stderr,lino,"unknown relatioship",relationship
				exit()				
				
			for par in thisParent:
				targetSet.add(par)

		#now this to form a parent
		parent[thisIdent]=GOs
		prevIdent=thisIdent


	fil.close()

	#now output
	for termID,termStruct in terms.items():
		name,is_a,part_of,other=termStruct
		outStr=termID+" = "+name+" "  #need a two space
		if len(is_a)>0:
			outStr+=" [isa: "+" ".join(is_a)+" ]"
		if len(part_of)>0:
			outStr+=" [partof: "+" ".join(part_of)+" ]"
		if len(other)>0:
			outStr+=" [other: "+" ".join(other)+" ]"

		print >> stdout, outStr


		
def ensureTermExists(GOTree,TermID,TermDesc):
	
		
	try:
		newTerm=GOTree[TermID]
		#print >> sys.stderr,"term",TermID,TermDesc,"already existed"
						
	except KeyError:
		#this is expected
		newTerm=dict()
		newTerm["desc"]=""
		newTerm["parents"]=[]
		newTerm["children"]=[]
		newTerm["id"]=TermID
		newTerm["markedparents"]=[]
		newTerm["visited"]=False
		GOTree[TermID]=newTerm	
	
	if len(TermDesc)>0:
		newTerm["desc"]=TermDesc		

	return newTerm


def pop_front(L):
	return L.pop(0)

def is_empty(L):
	return len(L)==0

def find_roots(GOTree):
	roots=[]
	for node in GOTree.values():
		if len(node["parents"])==0:
			roots.append(node)

	return roots

def is_marked(node):
	return node.has_key("marked") and node["marked"]==True

def get_marked_parents(node):
	try:
		if is_marked(node):
			return node["markedparents"]+[node]
		else:
			return node["markedparents"]
	except KeyError:
		return []

def addToL1(L1,L2):
	for l2 in L2:
		if l2 not in L1:
			L1.append(l2)


def validateMarkedTermsAreNotParentOfOtherPerRoot(root):
	Q=[]
	Q.append(root)

	NonValidatedChildren=[]

	while not is_empty(Q):
		u=pop_front(Q)
		u_marked=is_marked(u)
		markedparents=get_marked_parents(u)
		if(u["visited"]==True):
			continue

		u["visited"]=True
	
		#queue children
		for child in u["children"]:
			addToL1(child["markedparents"],markedparents)
			if is_marked(child) and len(markedparents)>0:
				#collapse
				NonValidatedChildren.append(child)			
	
			Q.append(child)


	return NonValidatedChildren


def getSubTreeNodesBFS(root):
	
	nodes=[]
	nodesID=[]

	Q=[]
	Q.append(root)
	
	#NonValidatedChildren=[]

	while not is_empty(Q):
		u=pop_front(Q)
		
		if(u.has_key("visited.BFS") and u["visited.BFS"]):
			continue
	
		u["visited.BFS"]=True
		
		nodes.append(u)
		nodesID.append(u["id"])
		
		#queue children
		for child in u["children"]:
			Q.append(child)

	for node in nodes:
		del node["visited.BFS"]
	return (nodes,nodesID)

def getAllAncestorsOfNodeBFS(root):
	nodes=[]
	nodesID=[]

	Q=[]
	Q.append(root)
	
	#NonValidatedChildren=[]

	while not is_empty(Q):
		u=pop_front(Q)
		
		if(u.has_key("visited.BFS") and u["visited.BFS"]):
			continue
	
		u["visited.BFS"]=True
		
		nodes.append(u)
		nodesID.append(u["id"])
		
		#queue children
		for parent in u["parents"]:
			Q.append(parent)

	for node in nodes:
		del node["visited.BFS"]
	return (nodes,nodesID)

			

def validateMarkedTermsAreNotParentOfOther(GOTree,Terms):
	for term in Terms:
		if not GOTree.has_key(term):
			print >> sys.stderr,"term",term,"non-existent"
			#return False
			continue

		GOTree[term]["marked"]=True
	
	NonValidatedChildren=[]
	
	#now BFS
	roots=find_roots(GOTree)
	
	for root in roots:
		NonValidatedChildren.extend(validateMarkedTermsAreNotParentOfOtherPerRoot(root))

	return NonValidatedChildren	


	
	#cleanUp?
#	for term in Terms:
#		del GOTree[term]["marked"]
	

def readInGOTree(fil):
	GOTree=dict()
	#fil=open(filename)
	for lin in fil:
		lin=lin.strip()
		if lin[0]=="(":
			continue		
		fields=lin.split("  ")
		#print >> sys.stderr, fields
		thisTerm=fields[0].split("=")
		if len(thisTerm)<2:
			continue

		thisTermID=thisTerm[0].strip()
		thisTermDesc=thisTerm[1].strip()
		
		thisTerm=ensureTermExists(GOTree,thisTermID,thisTermDesc)
		

		if len(fields)==1:
			continue

		fields=fields[1].split("[")

		for field in fields:
			links=field.split(" ")
			linkName=links[0]
			if len(linkName)<1:
				continue
			
			if linkName!="isa:" and linkName!="partof:" and linkName!="other:":
				print >> sys.stderr,"linkName unknown:",linkName
				continue
			
			for link in links[1:]:
				if len(link)<1 or link.strip()=="]":
					continue
				
				linkedTerm=ensureTermExists(GOTree,link,"")
				thisTerm["parents"].append(linkedTerm) #link
				linkedTerm["children"].append(thisTerm) #thisTermID
	
			
				

	fil.close()

	return GOTree


def loadWishList(fin):
	L=[]

	for lin in fin:
		L.append(lin.strip())
	

	fin.close()
	return L

def fillTerms(terms):
	for i in range(0,len(terms)):
		terms[i]=fillTerm(terms[i])

	return terms

def fillTerm(term):
	lterm=len(term)
	if lterm<7:
		for i in range(0,7-lterm):
			term="0"+term

	return term


def printUsageAndExit(programName):
	print >> sys.stderr,programName
	print >> sys.stderr,"--all-descendents gofile termid"
	print >> sys.stderr,"--all-ancestors gofile termid"
	print >> sys.stderr,"--expand-goa gofile goafile"
	print >> sys.stderr,"--geneontologyorg2bingo geneontologyorggofile"
	print >> sys.stderr,"--geneontologyorgobo1_2_2bingo OBO1_2formatedgeneontologyfile"
	print >> sys.stderr,"--classify-namespace OBO1_2formatedgeneontologyfile"
	sys.exit()

#RECK	0004867	IEA
#RECK	0045786	IEA
#RECK	0005515	IPI
#CCNO	0008152	IEA
#CCNO	0005634	IEA
#CCNO	0045008	EXP

def reannoateGOAToFullGOA(GOTree,filename):
	GOA=dict()  #GOA[geneName]=[[term,..],[evidence,]]
	fil=open(filename)
	for lin in fil:
		lin=lin.strip()
		fields=lin.split("\t")
		geneName,term,evidence=fields
		try:
			thisTerms,thisEvidence=GOA[geneName]
		except:
			thisTerms=[]
			thisEvidence=[]
			GOA[geneName]=[thisTerms,thisEvidence]
		
		if term not in thisTerms:
			thisTerms.append(term)
			thisEvidence.append(evidence)

				

	fil.close()
	#done reading
	#now go to each gene and each term and find all parents and append terms if not existed
	nGenes=len(GOA)	
	iGene=0
	for geneName,term_evidence in GOA.items():
		iGene+=1		
		print >> sys.stderr,"processing gene",iGene,"of",nGenes,":",geneName
		thisTerms,thisEvidence=term_evidence
		newTerms=set()
		for perTerm,perEvidence in zip(thisTerms,thisEvidence):
			(ancestor_tree,ancestor_tree_id)=getAllAncestorsOfNodeBFS(GOTree[perTerm])	
			for ancestral_id in ancestor_tree_id:
				if ancestral_id not in thisTerms:
					newTerms.add(ancestral_id)
			
			print >> sys.stdout,geneName+"\t"+perTerm+"\t"+perEvidence #now output original term-lines

		#now output the new ones
		
		for perNew in newTerms:
			print >> sys.stdout,geneName+"\t"+perNew+"\t"+"ANC"
			
		
	
		
if __name__=="__main__":
	#debug
	
	programName=sys.argv[0]

	if len(sys.argv)==1:
		printUsageAndExit(programName)
	opts,args=getopt(sys.argv[1:],'',['all-descendents','all-ancestors','expand-goa',"geneontologyorg2bingo","geneontologyorgobo1_2_2bingo",'classify-namespace'])
	

	for o,v in opts:
		if o=='--all-descendents':
			anno,term=args
				

			GOTree=readInGOTree(open(anno))
			(subtree,subtree_id)=getSubTreeNodesBFS(GOTree[term])
			for node in subtree:
				print >> sys.stdout, node["id"], node["desc"]

		elif o=='--all-ancestors':
			anno,term=args
				

			GOTree=readInGOTree(open(anno))
			(subtree,subtree_id)=getAllAncestorsOfNodeBFS(GOTree[term])
			for node in subtree:
				print >> sys.stdout, node["id"], node["desc"]			
		elif o=='--expand-goa':
			anno,goafile=args
			GOTree=readInGOTree(open(anno))
			reannoateGOAToFullGOA(GOTree,goafile)					
		elif o=="--geneontologyorg2bingo":
			filename,=args
			convertGeneOntologyOrgToBinGOGO(filename)
		elif o=="--geneontologyorgobo1_2_2bingo":
			filename,=args
			convertGeneOntologyOrgOBO1_2FileToBinGO(filename)
		elif o=='--classify-namespace':
			filename,=args
			getNamespaceListFromOBO1_2File(filename)

		
	sys.exit()	
	###not executed from this point on

	GOTree=readInGOTree(open("/net/coldfact/data/awcheng/genomes/hg18/xref/BiNGO.a/GO_Full"))
	#print >> sys.stdout, GOTree
	print >> sys.stdout, "roots"
	roots=find_roots(GOTree)
	print >> sys.stdout,"*****"
	for root in roots:
		print >> sys.stdout,root["id"],root["desc"]

	NonValid=validateMarkedTermsAreNotParentOfOther(GOTree,["0031012","0007160","0005581","0007229","0005604"])
		
	for NonV in NonValid:
		print >> sys.stdout,"NonValid",NonV["id"],NonV["desc"],"par:"
		for markedparent in NonV["markedparents"]:
			print >> sys.stdout,"\t", markedparent["id"],markedparent["desc"]

		print >> sys.stdout,"";
