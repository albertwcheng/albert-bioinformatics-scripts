#!/usr/bin/env python

from albertcommon import *
from getopt import getopt
from sys import *
from math import *
from types import *

def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"[Options] filename logics"
	print >> stderr,"Open file and evaluate logic per line, print line if logic is true"
	print >> stderr,"logic can form using python code (math library also available). with addition feature:"
	print >> stderr,"[SYSTEMVAR] refers to a value provided by the script. see SYSTEMVAR below"
	print >> stderr,"[x] can refers to column selector. e.g., [2] refers to value at column 2. [.GeneName] refers to value at column GeneName"
	print >> stderr,"force conversion to type T by T([x]). T = [float|int|str] see --autoconv"
	print >> stderr,"Options:"
	print >> stderr,"--autoconv [float*|int|str|off] automatic attempt to convert into a type for each field"
	print >> stderr,"--line-out pythoncode .specify what to output ,can use tuple e.g., [2],[3],[5] would be fields 2 3 and 5. Default is LINE, i.e., the whole line"
	print >> stderr,"--print-compiled-logics. print out the compiled logics to stderr"
	print >> stderr,"SYSTEMVAR:"
	print >> stderr,"FNR current line number"
	print >> stderr,"LINE current whole line content"
	
	explainColumns(stderr)
	exit()
	
def autoconv(x,conversion):
	try:
		return eval(conversion+"(x)")
	except:
		return x


def compileLogics(logics,header,autoconvertor):
	#find all [p]
	colSelectorOpen=False
	compiledLogics=""
	for s in logics:
		if colSelectorOpen:
			if s==']':
				colSelectorOpen=False
				selectedCols=getCol0ListFromCol1ListStringAdv(header,selectorStr)
				selectedCol=selectedCols[0]
				if len(selectedCols)>1:
					#warn
					print >> stderr,"Warning:",selectorStr," selects multiple columns. Use only the first one @",selectedCol,":",header[selectedCol]
				compiledLogics+="autoconv(fields["+str(selectedCol)+"],'"+autoconvertor+"')"
					
			else:
				selectorStr+=s
		else: #colSelectorOpen==FALSE
			if s=='[':
				colSelectorOpen=True
				selectorStr=""
			else:
				compiledLogics+=s
	
	return compiledLogics

if __name__=="__main__":
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['fs=','header-row=','start-row=','autoconv=','line-out=','print-compiled-logics'])
	
	fs="\t"
	headerRow=1
	startRow=2
	autoconvertor="float"
	lineOut="LINE"
	printCompiledLogics=False
	
	for o,v in opts:
		if o=='--fs':
			fs=v
		elif o=='--header-row':
			headerRow=int(v)
		elif o=='--start-row':
			startRow=int(v)
		elif o=='--autoconv':
			autoconvertor=v
		elif o=='--line-out':
			lineOut=v
		elif o=='--print-compiled-logics':
			printCompiledLogics=True
			
	try:
		filename,logics=args
	except:
		printUsageAndExit(programName)
	
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	
	compiledLogics=compileLogics(logics,header,autoconvertor)
	compiledLineOut=compileLogics("("+lineOut+")",header,"str")
	
	if printCompiledLogics:
		print >> stderr, compiledLogics
		print >> stderr, compiledLineOut
	
	exit
	
	lino=0
	
	fil=open(filename)
	for lin in fil:
		lino+=1
		FNR=lino	 #system var FNR
		lin=lin.rstrip("\r\n")
		LINE=lin     #system var LINE
		
		
		#evaluate the logic. if true, print line
		fields=lin.split(fs)
		
		if lino>=startRow:
			try:
				logicResult=eval(compiledLogics)
			except:
				print >> stderr,"logic error at line "+str(lino)+":"+str(fields)
				exit()
		else:
			logicResult=True
				
		if logicResult:
			outResult=eval(compiledLineOut)
			if type(outResult) in (ListType,TupleType):
				outResult=fs.join(outResult)
			
			print >> stdout,outResult
		
	fil.close()