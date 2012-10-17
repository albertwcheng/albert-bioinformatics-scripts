#!/usr/bin/env python

import re
from albertcommon import *
from sys import *

'''

                        R = G or A
                        Y = C or T
                        M = A or C
                        K = G or T
                        S = G or C
                        W = A or T
                        B = not A (C or G or T)
                        D = not C (A or G or T)
                        H = not G (A or C or T)
                        V = not T (A or C or G)
                        N = A or C or G or T
                        
'''

patternMap={
	"R" => "[GA]"
	"Y" => "[CT]"
	"M" => "[AC]"
	"K" => "[GT]"
	"S" => "[GC]"
	"W" => "[AT]"
	"B" => "[CGT]"
	"D" => "[AGT]"
	"H" => "[ACT]"
	"V" => "[ACG]"
	"N" => "[ACGT]"	
}

def recSeqToRegex(recSeq,notConvertedSet):
	regx=""
	
	for a in recSeq:
		if a in ['A','C','T','G']:
			regx+=a
		elif a in patternMap:
			regx+=patternMap[a]
		else:
			if notConvertedSet:
				notConvertedSet.add(a)
			
	return regx
	
def readRebaseFile(filename):
	fil=open(filename)
	
	REBase=[]
	notConvertedSet=set()
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split("\t")
		if len(fields)<6:
			continue
		
		enzymeName,prototype,recSeq,methylationSite,commSource,refs=fields
		REBase=fields
		regxString=recSeqToRegex(recSeq,notConvertedSet)
		regxObj=re.compile(regxString)
		REBase+=[regxString,regxObj]
		
		
	
	fil.close()
	
	return REBase

def searchRestrictionEnzymes(seq,REBase)
	founds=dict()
	for REBaseRecord in REBase:
		enzymeName=REBase[0]
		regxObj=REBase[-1]
		regxString=REBase[-2]
		
		matchObjs=regxObj.findAll(seq)
		founds[enzymeName]=[regexObj,regxString,matchObjs]
		
def getSeqFromMatchObj(seq,matchObj):
	return seq[matchObj.start():matchObj.end()]
	
#REName/matchSeq/position
if __name__=='__main__':
	
	