#!/usr/bin/env python

from operator import itemgetter
from sys import *
from getopt import getopt
from albertcommon import *

NEBEnzymes={'SpeI':'ACTAGT','XhoI':'CTCGAG','SalI':'GTCGAC','XbaI':'TCTAGA','ApaI':'GGGCCC'}

def getRestrictionFragmentsCircular(enzymesPos,sizeV):
	fragments=[]
	enzymesPosSorted=sorted(enzymesPos,key=itemgetter(1))
	L=len(enzymesPosSorted)
	for i in range(0,L-1):
		for j in range(i+1,L):
			enzyme1,pos1=enzymesPosSorted[i]
			enzyme2,pos2=enzymesPosSorted[j]
			centralsize=pos2-pos1+1
			othersize=sizeV-centralsize
			fragments.append(((enzyme1,pos1),(enzyme2,pos2),centralsize))
			fragments.append(((enzyme2,pos2),(enzyme1,pos1),othersize))
	return fragments
	
def getLocationsOfCut(seq,recogs):
	locs=[]
	for enzymeName,recogseq in recogs:
		locations=String_findAll(seq,recogseq)
		for location in locations:
			locs.append((enzymeName,location+1))
	
	return locs
		
def printUsageAndExit(programName):
	print >> stderr,programName,"[options] infile > outfile"
	print >> stderr,"options:"
	print >> stderr,"--in-pos  infile is a position file #size<tab>sizeOfVector followed by <enzymeName><tab><pos1>"
	print >> stderr,"--in-seq  infile is a sequence file"
	print >> stderr,"--add-recog  enzymeName,consensus. add a cutting consensus"
	print >> stderr,"--add-nebzymes enz1,enz2,... . add NEBEnzyme(s)"
	exit(1)

if __name__=="__main__":
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['in-pos','in-seq','add-recog=','add-nebzymes='])
	
	inpos=True
	sizeV=-1
	
	recogs=[]
	
	for o,v in opts:
		if o=='--in-pos':
			inpos=True
		elif o=='--in-seq':
			inpos=False #implies sequence
		elif o=='--add-recog':
			enzymeName,recogseq=v.split(",")
			recogs.append((enzymeName,recogseq.upper()))
		elif o=='--add-nebzymes':
			enzymeNames=v.split(",")
			for enzymeName in enzymeNames:
				recogs.append((enzymeName,NEBEnzymes[enzymeName]))	
	try:
		infile,=args
	except:
		printUsageAndExit(programName)
	
	enzymesPos=[]
	
	
	if inpos:
		
		fil=open(infile)
		for lin in fil:
			lin=lin.rstrip("\r\n")
			enzymeName,pos=lin.split("\t")
			pos=int(pos)
			if enzymeName=="#size":
				sizeV=pos
			else:
				enzymesPos.append((enzymeName,pos))
		
		fil.close()
	else:
		seq=""
		fil=open(infile)
		for lin in fil:
			lin=lin.rstrip("\r\n")
			if len(lin)<1:
				continue
			
			if lin[0]==">": #header, skip
				continue
			
			seq+=lin.upper()
				
		fil.close()	
		
		sizeV=len(seq)
		enzymesPos=getLocationsOfCut(seq,recogs)
		#print >> stderr,enzymesPos
		
	if sizeV<0:
		print >> stderr,"invalid sizeV=",sizeV,".Please specify if using --in-pos option by a line with #size<tab>sizeV"
		exit(1)
	
	if len(enzymesPos)<2:
		print >> stderr,"has < 2 enzymePos"
		exit(0)
	
	
	fragments=getRestrictionFragmentsCircular(enzymesPos,sizeV)
	
	#first sort by size
	fragments.sort(key=itemgetter(2),reverse=True)
	#now print
	for fragment in fragments:
		enpos1,enpos2,sizefrag=fragment
		enzyme1,pos1=enpos1
		enzyme2,pos2=enpos2
		print >> stdout,str(sizefrag)+"\t"+enzyme1+"@"+str(pos1)+"\t"+enzyme2+"@"+str(pos2)
		
		