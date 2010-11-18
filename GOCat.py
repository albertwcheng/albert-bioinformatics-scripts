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

def main( GOFile, FgFile, FgTermCol,FgStartRow1, TermsFile):
	global termSeperator;
	
	GOTree=readInGOTree(generic_istream(GOFile))
	Terms=fillTerms(loadWishList(generic_istream(TermsFile)))	
	
	TermsFreq=dict()
	for term in Terms:
		TermsFreq[term]=0.0

	TermFreq["Other"]=0.0

	global termSeperator;


	fil=generic_istream(FgFile);
	
	lino=0;
	for lin in fil:
		lino+=1;
		if(lino<startRow1):
			continue;
		lin=lin.rstrip("\r\n");
		spliton=lin.split("\t");
		if(len(spliton)<FgTermCol+1):
			#print >> stderr,"Invalid Col numbers, ignored:",lin;
			continue;
		
		nTermMarked=0

		ThisEntryTerms=spliton[FgTermCol].split(termSeperator);
		for term in ThisEntryTerms:
			if term in Terms:
				nTermMarked+=1
		
		if nTermMarked==0:
			TermFreq["Other"]+=1
		else:
			dividedPerGOTerm=1.0/nTermMarked
		
			for term in ThisEntryTerms:
				try:
					TermFreq[term]+=dividedPerGOTerm
				except KeyError:
					pass

	

	
	fil.close()
	
	print >> sys.stdout,"TermID\tTermDesc\tTermFreq"

	for termid,freq in TermFreq.items():
		print >> sys.stdout,"%s\t%s\t%f" %(termid,GOTree[termid]["desc"],freq)


def printUsage():
	print >> stderr, "Usage:",sys.argv[0],"GOFile FgFile FgTermCol1 FgStartRow1 TermsFile";
	print >> stderr, "Option";
	print >> stderr, "--term-sep=,";
	exit();


opts, argvs = getopt(sys.argv[1:],'',["term-sep="]);



for o,a in opts:
	if o=="--term-sep":
		termSeperator=a;


try:
	GOFile, FgFile, FgTermCol1, FgStartRow1, TermsFile = argvs;
except:
	printUsage();




main(GOFile, FgFile,int(FgTermCol1)-1,int(FgStartRow1),TermsFile);

