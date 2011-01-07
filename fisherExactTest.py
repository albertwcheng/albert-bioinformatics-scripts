#!/usr/bin/env python

import fisher
from sys import *
from albertcommon import *


'''

from http://pypi.python.org/pypi/fisher/0.1.4



>>> from fisher import pvalue
>>> mat = [[12, 5], [29, 2]]
>>> p = pvalue(12, 5, 29, 2)
>>> p.left_tail, p.right_tail, p.two_tail
(0.044554737835078267, 0.99452520602190897, 0.08026855207410688)
'''

def fisherExactPValues(t11,t12,t21,t22):
	return fisher.pvalue(t11,t12,t21,t22)
	
def fisherExactTwoTailPValue(t11,t12,t21,t22):
	return fisherExactPValues(t11,t12,t21,t22).two_tail


def fisherExactLeftTailPvalue(t11,t12,t21,t22):
	return fisherExactPValues(t11,t12,t21,t22).left_tail

def fisherExactRightTailPvalue(t11,t12,t21,t22):
	return fisherExactPValues(t11,t12,t21,t22).right_tail
	
def printUsageAndExit_fisherExactTest(programName):
	print >> stderr,programName,"--inline [pvaluetype=two|left|right|reportall] t11 t12 t21 t22"
	print >> stderr,programName,"--infile [pvaluetype=two|left|right] filename t11col t12col t21col t22col startRow > ofileOfPvalues"
	exit()
	
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		requestType=args[0]
		pvalueType=args[1]
	except:
		printUsageAndExit_fisherExactTest(programName)
		
	if requestType=="--inline":
		try:
			t11,t12,t21,t22=args[2:]
			t11=int(t11)
			t12=int(t12)
			t21=int(t21)
			t22=int(t22)
		except:
			print >> stderr,"invalid arguments for --inline",args[2:],".Abort"
			printUsageAndExit_fisherExactTest(programName)
			
		try:
			if pvalueType=="two":
				print >> stdout,fisherExactTwoTailPValue(t11,t12,t21,t22)
			elif pvalueType=="left":
				print >> stdout,fisherExactLeftTailPValue(t11,t12,t21,t22)
			elif pvalueType=="right":
				print >> stdout,fisherExactRightTailPValue(t11,t12,t21,t22)
			elif pvalueType=="reportall":
				pvalues=fisherExactPValues(t11,t12,t21,t22)
				print >> stdout,"2x2 table:"
				print >> stdout,t11,t12
				print >> stdout,t21,t22
				print >> stdout,"pvalues:"
				print >> stdout,"Two-tail:",pvalues.two_tail
				print >> stdout,"Left:",pvalues.left_tail
				print >> stdout,"Right:",pvalues.right_tail
			else:
				print >> stderr,"unknown pvalue type:",pvalueType,".Abort"
				printUsageAndExit_fisherExactTest(programName)
		except OverflowError:
			print >> stderr,"value too large to convert to int. Abort"
			exit()
	elif requestType=="--infile":
		try:
			filename,t11col,t12col,t21col,t22col,startRow=args[2:]
			startRow=int(startRow)
		except:
			print >> stderr,"invalid arguments for --infile",args[2:],".Abort"
			printUsageAndExit_fisherExactTest(programName)
		
		fs="\t"
		
		headerRow=max(1,startRow-1)
		header,prestarts=getHeader(filename,headerRow,startRow,fs)
		t11col=getCol0ListFromCol1ListStringAdv(header,t11col)[0]
		t12col=getCol0ListFromCol1ListStringAdv(header,t12col)[0]
		t21col=getCol0ListFromCol1ListStringAdv(header,t21col)[0]
		t22col=getCol0ListFromCol1ListStringAdv(header,t22col)[0]
		
		lino=0
		fil=open(filename)
		for lin in fil:
			lin=lin.rstrip("\r\n")
			lino+=1
			if lino<startRow:
				continue
			
			fields=lin.split(fs)
			
			try:
				t11=int(fields[t11col])
				t12=int(fields[t12col])
				t21=int(fields[t21col])
				t22=int(fields[t22col])
			except:
				print >> stderr,"number conversion error at line",lino,fields
				print >> stdout,"nan"
				continue #abort this, onto the next one
				
			try:
				if pvalueType=="two":
					print >> stdout,fisherExactTwoTailPValue(t11,t12,t21,t22)
				elif pvalueType=="left":
					print >> stdout,fisherExactLeftTailPValue(t11,t12,t21,t22)
				elif pvalueType=="right":
					print >> stdout,fisherExactRightTailPValue(t11,t12,t21,t22)
			except OverflowError:
				print >> stderr,"value too large to convert to int at line",lino,"[",t11,t12,t21,t22,"]"
				print >> stdout,"nan"
		fil.close()
	else:
		print >> stderr,"unknown request type",requestType,".Abort"
		printUsageAndExit_fisherExactTest(programName)
		
			