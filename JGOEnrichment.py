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

import warnings;
warnings.simplefilter('ignore', DeprecationWarning);

import hypergeom;
from hypergeom import pvalue_enrichment;
from getopt import getopt
import shelve;
import sys;
from sys import stderr, stdout;

termSeperator=",";

from JHypergeometricPvalue import JHypergeometricPvalue





def calTerms(TERMS,filename,GeneIDCol,TermCol,startRow1,allowDuplicate):
	global termSeperator;
	
	genes=set()
	
	nTerms=0;
	nGenes=0;	

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
		
				
		incNGenes=False;


		ThisID=spliton[GeneIDCol];
		ThisEntryTerms=spliton[TermCol].split(termSeperator);
		for term in ThisEntryTerms:
			term=term.strip();
			if(len(term)<1):
				continue;
			
			if not TERMS.has_key(term):
				nTerms+=1;				
				TERMS[term]=[];

			if allowDuplicate:
				TERMS[term].append(ThisID);
				incNGenes=True
			else:
				if not incNGenes and ThisID not in genes:
					incNGenes=True
					genes.add(ThisID)

				if ThisID not in TERMS[term]:
					
					incNGenes=True;
					TERMS[term].append(ThisID)

		if incNGenes:
			nGenes+=1;

	
	TERMS["__$$$NGENES"]=nGenes;
	TERMS["__$$$NTERMS"]=nTerms;

def main(BgShelve, BgFile, BgGeneIDCol, BgTermCol, BgStartRow1, FgFile, FgGeneIDCol, FgTermCol,FgStartRow1,recomputeBg,useJava,allowDuplicate):
	global termSeperator;
	
	
	if not recomputeBg:
		saved=shelve.open(BgShelve);
		
		if not saved.has_key("BG"):
			recomputeBg=True;		
		else:
			BGData=saved["BG"];
			if len(BGData)<1 or not BGData.has_key("__$$$NGENES"):
				recomputeBg=True;

		saved.close();

	if recomputeBg:
		print >> stderr, "recal BG";
		BGData=dict();#=shelve.open(BgShelve);
		calTerms(BGData,BgFile,BgGeneIDCol,BgTermCol,BgStartRow1,allowDuplicate);
		saved=shelve.open(BgShelve);
		saved["BG"]=BGData;
		saved.close();


	FGData=dict();
	calTerms(FGData,FgFile,FgGeneIDCol,FgTermCol,FgStartRow1,allowDuplicate);
	

	#now calculate GO enrichment and FDR

	FGTerms=FGData.keys();

	nTermsBG=BGData["__$$$NTERMS"];
	nGenesBG=BGData["__$$$NGENES"];
	nTermsFG=FGData["__$$$NTERMS"];
	nGenesFG=FGData["__$$$NGENES"];

	pvalueTermMap=dict();

	JavaInputMatrix=[]	

	for term in FGTerms:
		if "__$$$" in term:
			continue;

		if not BGData.has_key(term):
			print >> stderr, "Error: term",term,"not found in background";
			sys.exit()
		
		BGTermEntry=BGData[term];
		FGTermEntry=FGData[term];

		pop=nGenesBG;
		popt=len(BGTermEntry);
		sam=nGenesFG;
		samt=len(FGTermEntry);
		
		#pvalue=pvalue_enrichment(pop,popt,sam,samt);
		
		#if not pvalueTermMap.has_key(pvalue):
		#	pvalueTermMap[pvalue]=[];
		
		#resultVector=[term,pop,popt,sam,samt,FGTermEntry]

		JavaInputMatrix.append([samt,sam,popt,pop,FGTermEntry,term])
		

		#print >> stderr, resultVector,",pvalue=",pvalue;
	
	JavaPvalues=JHypergeometricPvalue(JavaInputMatrix,-1)
	
	if len(JavaPvalues)==0:
		print >> stderr,"JPvalue error";
		sys.exit()

	for resultVector,pvalue in zip(JavaInputMatrix,JavaPvalues):
		
		
		if not pvalueTermMap.has_key(pvalue):
			pvalueTermMap[pvalue]=[];
		
		pvalueTermMap[pvalue].append(resultVector);
		print >> stderr, resultVector,",pvalue=",pvalue;

	#now sort pvalue and calculate FDR
	pvalues=sorted(pvalueTermMap.keys());
	
	nInc=0;
	
	print >> stdout, "FDR","\t",
	print >> stdout, "p-value","\t",
	print >> stdout, "term","\t",
	print >> stdout, "popt","\t",
	print >> stdout, "pop", "\t",
	print >> stdout, "popt/pop","\t",
	print >> stdout, "samt","\t",
	print >> stdout, "sam","\t",
	print >> stdout, "samt/sam", "\t",
	print >> stdout, "genes","\t";

	for pvalue in pvalues:
		termsWithThisPvalue=pvalueTermMap[pvalue];
		nTermsWithThisPvalue=len(termsWithThisPvalue);
				
		nInc+=nTermsWithThisPvalue;

		FDR=min(1.0,(pvalue*nTermsFG)/nInc);

		#now print;
		
		
		
		
		for termEntry in termsWithThisPvalue:
			
			#[samt,sam,popt,pop,FGTermEntry,term]

			samt,sam,popt,pop,FGTermEntry,term=termEntry;

			print >> stdout, FDR,"\t",
			print >> stdout, pvalue,"\t",
			print >> stdout, term,"\t",
			print >> stdout, popt,"\t",
			print >> stdout, pop, "\t",
			print >> stdout, float(popt)/pop,"\t",
			print >> stdout, samt,"\t",
			print >> stdout, sam,"\t",
			print >> stdout, float(samt)/sam, "\t",
			print >> stdout, ",".join(FGTermEntry),"\t";

	#BGData.close();


def printUsage():
	print >> stderr, "Usage:",sys.argv[0],"BgShelve BgFile BgGeneIDCol1 BgTermCol1 BgStartRow1 FgFile FgGeneIDCol1 FgTermCol1 FgStartRow1";
	print >> stderr, "Option";
	print >> stderr, "--term-sep=,";
	print >> stderr, "--force-recompute-bg";
	print >> stderr, "[--no-duplicate], --allow-duplicate";
	exit();


opts, argvs = getopt(sys.argv[1:],'',["term-sep=","force-recompute-bg","use-java","use-c","no-duplicate","allow-duplicate"]);

recomputeBg=False;

allowDuplicate=False
useJava=True

for o,a in opts:
	if o=="--force-recompute-bg":
		recomputeBg=True;
	elif o=="--term-sep":
		termSeperator=a;
	elif o=="--use-java":
		useJava=True
	elif o=="--use-c":
		useJava=False
	elif o=="--allow-duplicate":
		allowDuplicate=True
	elif o=="--no-duplicate":
		allowDuplicate=False

try:
	BgShelve, BgFile, BgGeneIDCol1, BgTermCol1, BgStartRow1, FgFile, FgGeneIDCol1, FgTermCol1, FgStartRow1 = argvs;
except:
	printUsage();




main(BgShelve,BgFile,int(BgGeneIDCol1)-1,int(BgTermCol1)-1,int(BgStartRow1),FgFile,int(FgGeneIDCol1)-1,int(FgTermCol1)-1,int(FgStartRow1),recomputeBg,useJava,allowDuplicate);

