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

from sys import *
from getopt import getopt

#REF GENE TABLE
#-1	Xkr4.cSep07	chr1	-	3195863	3205824	3204882	3205110	2	3195863,3203519,	3197398,3205824, 	0 	Xkr4	cmpl 	cmpl 	-1,0,

programName=argv[0]
opt,args=getopt(argv[1:],'',['source=','element-separator=','replace=','with=','expand-parents','input-is-gene-pred','output-rename-list='])

source="."
elementSeparator="@"
replaceWith=["",""]
expandParents=False
GenePredFormatInput=False
outputRenameList=None
for o,v in opt:
	if o=="--source":
		source=v
	elif o=='--element-separator':
		elementSeparator=v
	elif o=='--replace':
		replaceWith[0]=v
	elif o=='--with':
		replaceWith[1]=v
	elif o=='--expand-parents':
		expandParents=True
	elif o=='--input-is-gene-pred':
		GenePredFormatInput=True
	elif o=='--output-rename-list':
		outputRenameList=v
try:
	filename,=args
except:
	print >> stderr,"Usage:",programName,"filename"
	print >> stderr,"[Options]"
	print >> stderr,"--source x [.] .set the source name to x"
	print >> stderr,"--element-separator s [@]. set the element separator to s. for example, x=@ => Enah@EXON1"
	print >> stderr,"--replace x --with y. Defaut: No replacement. for example, x=_ , y=@,  Transposase_14 => Transposase@14"
	print >> stderr,"--expand-parents. Allow only one parent per exon"
	print >> stderr,"--input-is-gene-pred. No bin info, only nine columns (http://genome.ucsc.edu/FAQ/FAQformat#format9). Default is RefGene Table Schema"
	print >> stderr,"--output-rename-list filename. Output the mapping from original name to renamed due to --replace x --with y option"
	exit()

print >> stdout,"##gff-version 3"

fil=open(filename)
lino=0

genes=dict()


def within(x,left,right):
	return x>=left and x<=right

def formAttributeList(D):
	keyvaluepairs=[]
	for k,v in D.items():
		keyvaluepairs.append(k+"="+",".join(v))

	return ";".join(keyvaluepairs)

orderedGenes=[]


if outputRenameList:
	outputRenameList=open(outputRenameList,"w")

for lin in fil:
	lino+=1	
	if lino%1000==1:
		print >> stderr,"processing line",lino
	fields=lin.rstrip("\r\n").split("\t")
	try:
		if GenePredFormatInput:
			transcriptname,chrom,strand,start,end,cdsstart,cdsend,numexons,exonstarts,exonends=fields
			genename=".".join(transcriptname.split(".")[:-1])
		else:
			dummy,transcriptname,chrom,strand,start,end,cdsstart,cdsend,numexons,exonstarts,exonends,score,genename,dum2,dum3,frames=fields
		if replaceWith[0]!="":
			origGeneName=genename
			origTranscriptName=transcriptname
			for r,t in zip(replaceWith[0],replaceWith[1]):
				genename=genename.replace(r,t)
				transcriptname=transcriptname.replace(r,t)
			print >> outputRenameList,origGeneName+"\t"+genename
			print >> outputRenameList,origTranscriptName+"\t"+transcriptname
			
	except:
		print >> stderr,"error parsing line",lino,":",fields
		exit()

	exonstarts=exonstarts.split(",")
	exonends=exonends.split(",")
	
	try:
		geneinfo=genes[genename]
	except KeyError:
		geneinfo=[chrom,source,"gene",1000000000,0,".",strand,".",{"ID":[genename],"Name":[genename]},[],dict(),[]]
		genes[genename]=geneinfo
		orderedGenes.append(genename)
	
	#do sth for this transcript
	start=int(start)+1
	end=int(end)
	cdsstart=int(cdsstart)+1
	cdsend=int(cdsend)

	geneinfo[3]=str(min(start,int(geneinfo[3])))
	geneinfo[4]=str(max(end,int(geneinfo[4])))
	
	mRNAs=geneinfo[9]
	exons=geneinfo[10]
	cds=geneinfo[11]

	mRNAs.append([chrom,source,"mRNA",str(start),str(end),".",strand,".",{"ID":[transcriptname],"Parent":[genename]}])


	cdsstate=-1
	
	numR=len(exonstarts)
	if len(exonstarts)!=len(exonends):
		print >> stderr,"Error in RefGeneTable. Abort. fields=",fields
		exit()
	
	for i in range(0,numR):
		#frame=frames[i] #useless
		estart=exonstarts[i]
		eend=exonends[i]
	
		if len(estart)==0 or len(eend)==0:
			break

		estart=int(estart)+1
		eend=int(eend)
		if expandParents:
			ekey=transcriptname+"_"+str(estart)+"_"+str(eend)
		else:
			ekey=str(estart)+"_"+str(eend)

		length=eend-estart+1

		
		if strand in ["+","-"]:
		
			if cdsstate==-1:
				if within(cdsstart,estart,eend):
					cdsstate=0
					if strand=="+":
						phase=(cdsstart-estart)%3
						phase_nextadd=(length-phase)%3
					else:
						phase=(eend-cdsstart+1)%3

					
						
			elif cdsstate==0:
				if strand=="+":
					phase+=phase_nextadd
					phase_nextadd=(length-phase)%3
				else:
					phase+=length%3

				#if within(cdsend,estart,eend):
				#	cdsstate=1

			

			if cdsstate == 0: #in [0,1]:
				phase%=3
				thisCDSStart=max(cdsstart,estart) 
				thisCDSEnd=min(cdsend,eend)
				
				cds.append([chrom,source,"CDS",str(thisCDSStart),str(thisCDSEnd),".",strand,str(phase),{"ID":[genename+elementSeparator+"CDS"+str(len(cds)+1)],"Parent":[transcriptname]}])
				

			#new to correct for CDS starting and ending in the same exon
			if within(cdsend,estart,eend):
				cdsstate=2

			#if cdsstate==1:
			#	cdsstate=2


		try:		
			exonRecord=exons[ekey]
		except KeyError:
			#exon not existed
			exonRecord=[chrom,source,"exon",str(estart),str(eend),".",strand,".",{"ID":[genename+elementSeparator+"EXON"+str(len(exons.values())+1)],"Parent":[]}]
			exons[ekey]=exonRecord
		
		exonAttributes=exonRecord[8]
		exonAttributes["Parent"].append(transcriptname)

if outputRenameList:
	outputRenameList.close()		
		
fil.close()

def printGffRecord(to,record):
	recordDup=record[0:9]
	recordDup[8]=formAttributeList(recordDup[8])
	print >> stdout,"\t".join(recordDup)

#for geneName,geneInfo in genes.items():
for geneName in orderedGenes:
	geneInfo=genes[geneName]
	#now print gene info
	printGffRecord(stdout,geneInfo)
	mRNAs,exons,cdses=geneInfo[9:12]
	for mRNA in mRNAs:
		printGffRecord(stdout,mRNA)
	for ekey,exon in exons.items():
		printGffRecord(stdout,exon)
	for cds in cdses:
		printGffRecord(stdout,cds)


