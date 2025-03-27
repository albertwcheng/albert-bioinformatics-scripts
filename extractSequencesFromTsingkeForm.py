#!/usr/bin/env python3

from sys import *

def printUsageAndExit():
    print(argv[0]+" filename > out.txt",file=stderr)
    exit(0)

if len(argv)<2:
    printUsageAndExit()

filename=argv[1]

started=False
geneName=""

fil=open(filename)
for lin in fil:
    lin=lin.rstrip("\r\n")
    if(lin.startswith("基因名：")):
        geneName=lin.split("\t")[0].split("：")[1]
        seq=""
        continue
    if(lin.startswith("目标序列：")):
        seq=""
        started=True
        continue
    if(lin.startswith("销售总价：")):
        started=False
        if len(seq)>0:
            print(geneName+"\t"+seq,file=stdout)
        seq=""
        geneName=""
        continue
    if started:
        seq+=lin
fil.close()
        
