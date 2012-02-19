#!/usr/bin/env python

from sys import *

def parseValuePart(value):
	if value=="":
		return value
	val=""
	if value[0]=='"':
		quote='"'
		val=value[0]
	elif value[0]=="'":
		quote="'"
		val=value[0]
	else:
		quote=None
		if value[0] not in [" ","\t","#"]:
			val=value[0]
	
	level=0
	
	for v in value[1:]:
		if quote==None and v in [" ","\t","#"]:
			return val
		elif v==quote and level==0:
			return val+v
		elif v=="\\" and level==0:
			level=1
			val+=v
		else:
			level=0
			val+=v
	return val

def loadSettingFile(filename,keyvalsep="="):
	settings=dict()
	
	fil=open(filename)
	for lin in fil:
		lin=lin.strip("\r\n")
		
		if len(lin)<1 or lin[0]=="#":
			continue
		
		splits=lin.split(keyvalsep)
		key=splits[0].strip()
		value=keyvalsep.join(splits[1:]).strip()
		if len(key)==0:
			continue
		settings[key]=parseValuePart(value)
	
	fil.close()
	
	return settings

def printUsageAndExit(programName):
	print >> stderr,programName,"infile1 infile2"
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		infile1,infile2=args
	except:
		printUsageAndExit(programName)
	
	
	settings1=loadSettingFile(infile1)
	settings2=loadSettingFile(infile2)
	
	allkeys=list(settings1.keys())
	allkeys.extend(settings2.keys())
	allkeys=list(set(allkeys))
	allkeys.sort()
	
	
	NAValue="N/A"
	
	firstLine=True
	for key in allkeys:
		try:
			value1=settings1[key]
		except KeyError:
			value1=NAValue
	
		try:
			value2=settings2[key]
		except KeyError:
			value2=NAValue
			
		#it is impossible to get both NAValues
		if value1==value2:
			#the same, ignore
			continue
		
		if firstLine:
			print >> stdout,"key\t%s\t%s" %(infile1,infile2)
			firstLine=False
		
		print >> stdout,"%s\t%s\t%s" %(key,value1,value2)
		
	
			