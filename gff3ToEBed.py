#!/usr/bin/env python

'''
gff3

chr1    SE      gene    4772649 4775821 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-;Name=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-
chr1    SE      mRNA    4772649 4775821 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-
chr1    SE      mRNA    4772649 4775821 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.B;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-
chr1    SE      exon    4775654 4775821 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A.up;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A
chr1    SE      exon    4774032 4774186 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A.se;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A
chr1    SE      exon    4772649 4772814 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A.dn;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.A
chr1    SE      exon    4775654 4775821 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.B.up;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.B
chr1    SE      exon    4772649 4772814 .       -       .       ID=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.B.dn;Parent=chr1:4775654:4775821:-@chr1:4774032:4774186:-@chr1:4772649:4772814:-.B

1-based?

ebed

1) chrom
2) chrom start g0
3) chrom end g1
4) name
5) score
6) strand
7) thickStart = CDS Start g0
8) thickEnd = CDS End g1
9) itemRGB
10) blockCount = exonCount
11) blockSizes (,)
12) blockStarts (,) relative to Chom Start in 0-based

'''

#takes care of only the mRNA and exon record

from sys import *
from albertcommon import *
from getopt import getopt
from types import *
from operator import itemgetter


def parseAttributes(S):
	attributes=dict()
	keyvalues=S.split(";")
	for keyvalue in keyvalues:
		key,values=keyvalue.split("=")
		values=values.split(",")
		if len(values)==1:
			attributes[key]=values[0]
		else:
			attributes[key]=values
	
	return attributes



def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"[options] ingff > outebed"
	print >> stderr,"options"
	print >> stderr,"--itemRGB x. set item RGB to x, or use @@@@@ followed by Python logics to evaluate itemRGB dynamically. e.g., @@@@@'255,0,0' if name[-1]=='A' else '0,0,255'"
	print >> stderr,"--outGeneList outfile. output gene list to a file"
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['itemRGB=','outGeneList='])
	
	itemRGB="0,0,0"
	outGeneList=None
	
	for o,v in opts:
		if o=='--itemRGB':
			itemRGB=v
		elif o=='--outGeneList':
			outGeneList=v
	
	try:
		ingff,=args
	except:
		printUsageAndExit(programName)
	
	genes=dict() #(start1,end1,seqid,strand,score,id,children)
	mRNAs=dict() #(start1,end1,seqid,strand,score,id,parents,children)
	exons=dict() #(start1,end1,seqid,strand,score,id,parents)
	
	
	fil=open(ingff)
	lino=0
	for lin in fil:
		lino+=1
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=='#':
			continue
		
		fields=lin.split("\t")
		
		try:
			seqid,source,typex,start1,end1,score,strand,phase,attributes=fields
		except:
			print >> stderr,"invalid number of fields for line",lino,fields
			continue
		
		attributes=parseAttributes(attributes)
		#print >> stderr,attributes
		start1=int(start1)
		end1=int(end1)
		
		try:
			thisID=attributes["ID"]
		except KeyError:
			print >> stderr,"failed, object has no ID! @line",lino,attributes
			exit(1)
		
		try:
			parents=attributes["Parent"]
			if parents is not ListType:
				parents=[parents]
		except:
			parents=[]
		
		if typex=="gene":
			genes[thisID]=(start1,end1,seqid,strand,score,thisID,[])
		elif typex=="mRNA":
			#print >> stderr,"parent=",parents
			mRNAs[thisID]=(start1,end1,seqid,strand,score,thisID,parents,[])
		elif typex=="exon":
			exons[thisID]=(start1,end1,seqid,strand,score,thisID,parents)
		
		
		
		
	fil.close()
	
	#now rebuild children
	for thisID,mRNA in mRNAs.items():
		#thisID=mRNA[5]
		parents=mRNA[6]
		#print >> stderr,"parent of this mRNA",thisID,"are",parents
		for parent in parents:
			try:
				genes[parent][6].append(mRNA) #append the object
			except KeyError:
				print >> stderr,"no gene named",parent
				exit(1)
		
	for thisID,exon in exons.items():
		#thisID=exon[5]
		parents=exon[6]
		for parent in parents:
			try:
				mRNAs[parent][7].append(exon) #append the object
			except KeyError:
				print >> stderr,"no mRNA named",parent
	
	#now the structure is ok, produce ebed
	
	if outGeneList:
		fout=open(outGeneList,"w")
		for thisID,gene in genes.items():
			print >> fout,thisID
		fout.close()
	
	for name,mRNA in mRNAs.items():
		#sort the children
		gstart0=mRNA[0]-1
		gend1=mRNA[1]
		chrom=mRNA[2]
		#name=mRNA[5]
		score=mRNA[4]
		try:
			score=str(int(score))
		except:
			score="0"
			
		strand=mRNA[3]
		thickStart0=gstart0 #for now
		thickEnd1=gend1 #for now
		exons=mRNA[7]
		blockCount=len(exons)
		exons.sort(key=itemgetter(0)) #sort by exon start
		blockSizes=[]
		blockStarts=[]
		for exon in exons:
			estart0=exon[0]-1
			eend1=exon[1]
			esize=eend1-estart0
			blockStarts.append(str(estart0-gstart0))
			blockSizes.append(str(esize))
		
		
		if len(itemRGB)>=5 and itemRGB[0:5]=="@@@@@":
			thisItemRGB=eval(itemRGB[5:])
		else:
			thisItemRGB=itemRGB	
		
		#now output
		print >> stdout,"%s\t%d\t%d\t%s\t%s\t%s\t%d\t%d\t%s\t%d\t%s\t%s" %(chrom,gstart0,gend1,name,score,strand,thickStart0,thickEnd1,thisItemRGB,blockCount,",".join(blockSizes),",".join(blockStarts))
		
					
		
			
	