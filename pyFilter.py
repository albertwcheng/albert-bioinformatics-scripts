#!/usr/bin/env python

from albertcommon import *
from getopt import getopt
from sys import *
from math import *
from types import *
from numpy import *

def MEAN( *arguments ):
	_count=0
	_sum=0.0
	for argument in arguments:
		if type(argument)==ListType or type(argument)==TupleType:
			_sum+=sum(argument)
			_count+=len(argument)
		else:
			_sum+=argument
			_count+=1
		
	return _sum/_count
	


def ITEM(L,i):
	return L[i]

def log2(x):
	return log(x,2)

def stdN_1(L):
	return std(L,ddof=1)


__KEY_COUNT=dict()

def COUNTER( *arguments):
	global __KEY_COUNT
	t=[]
	for argument in arguments:
		t.append(argument)
	t=tuple(t)
	try:
		__KEY_COUNT[t]+=1
	except:
		__KEY_COUNT[t]=1
	
	
	#print >> stderr,t,__KEY_COUNT[t]
	return __KEY_COUNT[t]


def printUsageAndExit(programName):
	print >> stderr,"Usage:",programName,"[Options] filename logics"
	print >> stderr,"Open file and evaluate logic per line, print line if logic is true"
	print >> stderr,"logic can form using python code (math library also available). with addition feature:"
	print >> stderr,"[SYSTEMVAR] refers to a value provided by the script. see SYSTEMVAR below"
	print >> stderr,"[x] can refers to column selector. e.g., [2] refers to value at column 2. [.GeneName] refers to value at column GeneName"
	print >> stderr,"force conversion to type T by T([x]). T = [float|int|str] see --autoconv"
	print >> stderr,"Options:"
	print >> stderr,"--autoconv [float*|int|str|off] automatic attempt to convert into a type for each field"
	print >> stderr,"--line-out pythoncode .specify what to output for data rows,can use tuple e.g., [2],[3],[5] would be fields 2 3 and 5. Default is LINE, i.e., the whole line"
	print >> stderr,"--prestart-line-out pythoncode. specify what to output for prestart rows. Default is the same as line-out"
	print >> stderr,"--print-compiled-logics. print out the compiled logics to stderr"
	print >> stderr,"SYSTEMVAR:"
	print >> stderr,"FNR current line number"
	print >> stderr,"LINE current whole line content"
	print >> stderr,"ITEM(L,i) return L[i]"
	print >> stderr,"Extended Functions:"
	print >> stderr,"COUNTER(x) update and return the count for value x. Example COUNTER([1])==1 will print only the first row for each uniq value at column 1 producing a uniq operation on column 1 retaining order"
	
	explainColumns(stderr)
	exit()
	
def autoconv(x,conversion):
	try:
		return eval(conversion+"(x)")
	except:
		return x


def toStrList(L):
	sL=[]
	for x in L:
		sL.append(str(x))
	return sL
	
def compileLogics(logics,header,autoconvertor):
	#find all [p]
	colSelectorOpen=False
	compiledLogics=""
	for s in logics:
		if colSelectorOpen:
			if s==']':
				colSelectorOpen=False
				selectedCols=getCol0ListFromCol1ListStringAdv(header,selectorStr)
				
				if len(selectedCols)>1:
					#warn
					logicComponent=[]
					for selectedCol in selectedCols:
						logicComponent.append("autoconv(fields["+str(selectedCol)+"],'"+autoconvertor+"')")
					
					compiledLogics+="["+",".join(logicComponent)+"]"
				else:
					selectedCol=selectedCols[0]
					#print >> stderr,"Warning:",selectorStr," selects multiple columns. Use only the first one @",selectedCol,":",header[selectedCol]
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
	opts,args=getopt(argv[1:],'',['fs=','header-row=','start-row=','autoconv=','line-out=','print-compiled-logics','prestart-line-out='])
	
	fs="\t"
	headerRow=1
	startRow=2
	autoconvertor="float"
	lineOut="LINE"
	preStartLineOut=None
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
		elif o=='--prestart-line-out':
			preStartLineOut=v	
	try:
		filename,logics=args
	except:
		printUsageAndExit(programName)
	
	if not preStartLineOut:
		preStartLineOut=lineOut
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	
	compiledLogics=compileLogics(logics,header,autoconvertor)
	compiledLineOut=compileLogics("("+lineOut+")",header,autoconvertor)
	compiledPreStartLineOut=compileLogics("("+preStartLineOut+")",header,autoconvertor)
	
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
		NF=len(fields)
		if lino>=startRow:
			try:
				logicResult=eval(compiledLogics)
			except:
				print >> stderr,"logic error at line "+str(lino)+":"+str(fields)
				exit()
		else:
			#logicResult=True
			outResult=eval(compiledPreStartLineOut)
			if type(outResult) in (ListType,TupleType):
				outResult=fs.join(toStrList(outResult))
			print >> stdout,str(outResult)
			continue
				
		if logicResult:
			outResult=eval(compiledLineOut)
			if type(outResult) in (ListType,TupleType):
				outResult=fs.join(toStrList(outResult))
			
			print >> stdout,str(outResult)
		
	fil.close()