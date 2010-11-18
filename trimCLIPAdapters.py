#!/usr/bin/env python


'''

from Eric Wang

'''

import os,sys
from sys import *

ADP = 'TCGTATGCCGTCTTCTGCTTGT'
MINLEN = 15


def trimDir(indir,outdir):
    for f in os.listdir(indir):
        if not os.path.exists(outdir+f):
            trimFile(indir+f,outdir+f)


def trimFile(in_f,out_f):

    fh = open(in_f)
    line = fh.readline()
    seqs = {}
    i = 0
    while len(line)>0: 
        if line.startswith("@"):
            name = line[1:].strip()
            seq = fh.readline().strip()
            fh.readline()
            qual = fh.readline().strip()
            seqTrimmed,qualTrimmed = trimSeq(seq,qual)
            seqlen = len(seqTrimmed)
            if seqlen not in seqs:
                seqs[seqlen] = {}
            seqs[seqlen][seqTrimmed] = [name,qualTrimmed] #also collapsing by same sequence here
            line = fh.readline()
            i += 1
            if i%10000==0:
                print >> stderr, i

    out = open(out_f,'w')
    lengths = seqs.keys()
    lengths.sort()
    i = 1
    for l in lengths:
        for seq,name_qual in seqs[l].items():
            name,qual=name_qual
            out.write("@"+name+"\n"+seq+"\n"+"+"+name+"\n"+qual+"\n")
            i += 1
    out.close()

 
def trimSeq(seq,qual):
   
    newseq = seq
    newqual = qual
    for i in range(MINLEN,len(seq)-2):
        zipped = zip(seq[i:],ADP)
        numSame = sum([a==b for a,b in zipped])
        if float(numSame)/len(zipped)>0.8:
            newseq = seq[:i]
            newqual = qual[:i] 
		
    return newseq,newqual 


def plotSeqLengths(trimmed_f):
   
    fh = open(trimmed_f)
    line = fh.readline()
    lengths = {}
    while len(line)>0: 
        if line.startswith("+"):
            seq = fh.readline().strip()
            try: 
                lengths[len(seq)] += 1 
            except:
                lengths[len(seq)] = 1 
        line = fh.readline() 
    keys = lengths.keys()
    keys.sort()
    for k in keys:
        print >> stdout, k,lengths[k]
 
def printUsageAndExit(programName):
	print >> stderr, programName,"infile outfile"
	exit()

if __name__=="__main__":
	programName=argv[0]
	args=argv[1:]
	try:	
		infile,outfile=args
	except:
		printUsageAndExit(programName)

	trimFile(infile,outfile)
	plotSeqLengths(outfile)
