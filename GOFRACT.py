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

import warnings;
warnings.simplefilter('ignore', DeprecationWarning);

from getopt import getopt
import sys;
from sys import stderr, stdout;
from albertcommon import *
from ParseGOTree import *

termSeperator="|";


def calTerms(TERMS,filename,TermCol,startRow1):
	global termSeperator;


	fil=open(filename);
	ReqCol=max(GeneIDCol,TermCol);
	lino=0;
	for lin in fil:
		lino+=1;
		if(lino<startRow1):
			continue;
		lin=lin.rstrip("\r\n");
		spliton=lin.split("\t");
		if(len(spliton)<ReqCol+1):
			#print >> stderr,"Invalid Col numbers, ignored:",lin;
			continue;
		
		geneHasTerm=False;
		ThisID=spliton[GeneIDCol];
		ThisEntryTerms=spliton[TermCol].split(termSeperator);
		for term in ThisEntryTerms:
			term=term.strip();
			if(len(term)<1):
				continue;
			
			if not TERMS.has_key(term):
				nTerms+=1;				
				TERMS[term]=set();
			TERMS[term].add(ThisID);
			geneHasTerm=True;

		if(geneHasTerm):
			nGenes+=1;

	TERMS["__$$$NGENES"]=nGenes;
	TERMS["__$$$NTERMS"]=nTerms;

def main( GOFile, FgFile, ValueCol, FgTermCol,FgStartRow1, TermsFile, OnlyUnderTerm):
	global termSeperator;
	
	GOTree=readInGOTree(generic_istream(GOFile))
	Terms=fillTerms(loadWishList(generic_istream(TermsFile)))	
	
	TermsDict=dict()
	NewMatch=dict()
	
	
	(only_under_subtree,only_under_subtree_id)=getSubTreeNodesBFS(GOTree[OnlyUnderTerm])
	
	TermFreq=dict()
	for term in Terms:
		TermFreq[term]=0.0
		(a,b)=getSubTreeNodesBFS(GOTree[term])
		TermsDict[term]=b
		NewMatch[term]=-1

	TermFreq["Other"]=0.0

	global termSeperator;


	fil=generic_istream(FgFile);
	
	lino=0;
	for lin in fil:
		lino+=1;
		if(lino<FgStartRow1):
			continue;
		lin=lin.rstrip("\r\n");
		spliton=lin.split("\t");
		if(len(spliton)<FgTermCol+1):
			#print >> stderr,"Invalid Col numbers, ignored:",lin;
			continue;
		
		geneName=spliton[0]
		
		nTermMarked=0
		
		value=10**float(spliton[ValueCol])
		if value<1:
			continue
		
		ThisEntryTerms=spliton[FgTermCol].split(termSeperator);
		onlyunderOK=False
		#see whether complies with only-under rule:
		for term in ThisEntryTerms:
			term=term.split(":")[0]
			if term in only_under_subtree_id:
				onlyunderOK=True
				break
				
		if not onlyunderOK:
			continue
		
		
		for term in ThisEntryTerms:
			#print >> sys.stderr,term
			term=term.split(":")[0]
			
			#if term in Terms:
			for (term_to_test,childtermlist) in TermsDict.items():
				if term in childtermlist:
					nTermMarked+=1
					NewMatch[term_to_test]=lino
					if geneName=="RPL36AL":
						print >> sys.stderr,"term for RPL36AL",term_to_test
				#print >> sys.stderr,term,Terms 
		
		if geneName=="RPL36AL":
			print >> sys.stderr,"nTermMarked=",nTermMarked
			
		
		
		if nTermMarked==0:
			TermFreq["Other"]+=value
		else:

			dividedPerGOTerm=value/nTermMarked
			if geneName=="RPL36AL":
				print >> sys.stderr,"it was counted!",dividedPerGOTerm			
			#print >> sys.stderr,value,"contribute",dividedPerGOTerm
		
			for term in Terms:
				if NewMatch[term]==lino:
					TermFreq[term]+=dividedPerGOTerm
					#print >> sys.stderr,"adding",term,dividedPerGOTerm,"to",TermFreq[term]

	

	
	fil.close()
	
	print >> sys.stdout,"TermID\tTermDesc\tTermFreq"

	for termid,freq in TermFreq.items():
		if termid=="Other":
			desc="Other"
		else:
			desc=GOTree[termid]["desc"]
		print >> sys.stdout,"%s\t%s\t%f" %(termid,desc,freq)


def printUsage():
	print >> stderr, "Usage:",sys.argv[0],"GOFile FgFile ValueColSelector FgTermColSelector FgStartRow1 TermsFile OnlyUnderTerm";
	print >> stderr, "Option";
	print >> stderr, "--term-sep=,";
	exit();


opts, argvs = getopt(sys.argv[1:],'',["term-sep="]);



for o,a in opts:
	if o=="--term-sep":
		termSeperator=a;


try:
	GOFile, FgFile, ValueColSelector, FgTermColSelector, FgStartRow1, TermsFile, OnlyUnderTerm = argvs;
except:
	printUsage();

headerRow=1
fs="\t"
header,prestart=getHeader(FgFile,headerRow,headerRow,fs)
FgTermCol0=getCol0ListFromCol1ListStringAdv(header,FgTermColSelector)[0]
ValueCol0=getCol0ListFromCol1ListStringAdv(header,ValueColSelector)[0]



main(GOFile, FgFile,ValueCol0, FgTermCol0,int(FgStartRow1),TermsFile,OnlyUnderTerm);

