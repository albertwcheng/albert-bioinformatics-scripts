#!/usr/bin/python

'''
 collapseProbe.py

 This program collapse probe based on value
 Updated: Mar9 2009





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

import sys;
from getopt import getopt,GetoptError
from albertcommon import *
from math import *
from colStat import excelColIndex

exceptionFloatDefaultValue=1

suppressStrFloatErrorAbortion=False

def getGeneSets(geneSets,filename,idCols,startRow,FS):
	try:
		fil=generic_istream(filename)
	except IOError:
		print >> sys.stderr,"Cannot open",filename
		return
	
	lineOrderedKey=[]

	c=0;
	for lin in fil:
		lin=lin.rstrip();
		c+=1;
		


		if(startRow>c):
			#print>>sys.stdout, lin;
			continue;
		
		splitons=lin.split(FS);
		geneName=splitons[idCols[0]]

		if geneName=="":
			continue

		for i in range(1,len(idCols)):
			geneName+="|"+splitons[idCols[i]]

		#print >> sys.stderr,geneName

		if not geneSets.has_key(geneName):
			geneSets[geneName]=list();
			lineOrderedKey.append(geneName)

		geneSets[geneName].append(splitons);

	fil.close();	
	return lineOrderedKey


def getColumnVectors(_2Dmatrix):
	columnVectors=[]
	if len(_2Dmatrix)<1:
		return columnVectors

	ncols=len(_2Dmatrix[0])
	for i in range(0,ncols):
		L=[]
		columnVectors.append(L)
		for rowVector in _2Dmatrix:
			L.append(rowVector[i])

	return columnVectors

exceptionStrFloatCalled=False

def exceptionStrFloat(S):
	
	global exceptionStrFloatCalled
	global exceptionFloatDefaultValue

	if exceptionStrFloatCalled:
		return
	
	exceptionStrFloatCalled=True
	print >> sys.stderr,"Warning: String Conversion Exception",S

	#print >> sys.stderr,	suppressStrFloatErrorAbortion

	if not suppressStrFloatErrorAbortion:
		print >> sys.stderr,"aborted"
		sys.exit()
	else:
		print >> sys.stderr,"uses default failsafe value for invalid conservion",exceptionFloatDefaultValue
		
def StrVector2FloatVector(ListOfStr):
	global exceptionFloatDefaultValue;
	FloatVector=[]
	for S in ListOfStr:
		try:
			FloatVector.append(float(S))
		except:
			exceptionStrFloat(S)
			FloatVector.append(exceptionFloatDefaultValue)

	return FloatVector



def getIncludedCols(L,includes):
	newL=[]	
	for inc,l in zip(includes,L):
		if inc==1:
			newL.append(l)
	return newL

def getIncludesColsByIndexVector(L,includescols):
	newL=[]
	for col in includescols:
		newL.append(L[col])
	return newL


def collapseProbes(geneSets,lineOrderedKey,idCols,valueCols,minFilter,maxFilter,method,featureSel,specialColOps,FS,OFS,includes):


	
	NValues=len(valueCols)
	
	specialColOpsKey=specialColOps.keys()

	if method in [1,2,3] or featureSel in [1,2,3]:
		initValue=float(MIN_INT)
	else:
		initValue=float(MAX_INT)

	for geneName in lineOrderedKey:
		#print >> sys.stderr, "b4:", geneSets[geneName]
		repProbe=[]	
		if method in [5,6,7,8,17]: #vertical collapse methods
			columnVectors=getColumnVectors(geneSets[geneName])
			#print >> sys.stderr, "coV:\n",columnVectors
			ncolumns=len(columnVectors)
			for col in range(0,ncolumns):
				colfVector=[]
				if col in idCols: #added 4/14/2009
					repProbe.append(columnVectors[col][0])
				elif col in valueCols:
					colfVector=StrVector2FloatVector(columnVectors[col])					
					#print >> sys.stderr, colfVector
					if method in [7,8]:
						removeOutliers(colfVector)
					#print >> sys.stderr, "rx:",colfVector
					if method in [5,7]: #mean
						repProbe.append(str(meanOfList(colfVector)))
					elif method in [4,6,8]: #median: #added 8
						repProbe.append(str(medianOfList(colfVector)))
					elif method in [17]:
						repProbe.append(str(max(colfVector)))
					else:
						print >> sys.stderr,"unknown method",method
						exit()
					
				
				elif col in specialColOpsKey: #is a special column, need some treatment!
					methodOp,params=specialColOps[col]
					if methodOp in [5,6,7,8,9,10,13,14,15,16]:
						colfVector=StrVector2FloatVector(columnVectors[col])
					if methodOp in [7,8,14,15,16]:
						removeOutliers(colfVector)
					if methodOp in [5,7]:
						repProbe.append(str(meanOfList(colfVector)))
					elif methodOp in [6,8]:
						repProbe.append(str(medianOfList(colfVector)))
					elif methodOp in [9,16]:
						repProbe.append(str(percentileOfList(float(params[0]),colfVector)))
					elif methodOp==10:
						repProbe.append(str(countIfInRangeInc(float(params[0]),float(params[1]),colfVector)))
					elif methodOp==11:
						repProbe.append(str(countIf(params,columnVectors[col])))
					elif methodOp==13:
						#print >> sys.stderr, float(params[0]), colfVector
						repProbe.append(str(countIf(StrVector2FloatVector(params),colfVector)))
						
				else:
					repProbe.append(columnVectors[col][0]) #directly copy other columns
		
			#print >>sys.stderr, "XXXX:",repProbe
			geneSets[geneName]=[repProbe]

		repProbe=[]	
		feature=initValue
		
		
		#print >> sys.stderr, geneSets[geneName]

		for probe in geneSets[geneName]: #each row
			#print >> sys.stderr,"probe",probe
			sumXsq=0.0
			sumX=0.0
			#maxX=float(MIN_INT) #updated move out of for loop (on 11/9/2009)
			maxX=-1000.00 #float(MIN_INT)			
			
			for j in valueCols:
				try:
					X=float(probe[j])
				except:
					if not suppressStrFloatErrorAbortion:
						print valueCols,probe,j,geneName
						
						print >> sys.stderr,"Str->float Error: aborting:",probe[j]
						sys.exit()
					else:
						X=0
				sumX+=X
				sumXsq+=X**2
				if maxX<X:
					maxX=X
				
			mean_X=sumX/NValues
			mean_Xsq=sumXsq/NValues
			var_X=mean_Xsq-(mean_X)**2
			stddev_X=sqrt(var_X)

			if method==1 or featureSel==1: #maxMax
				if maxX>feature:
					feature=maxX
					repProbe=probe
			elif method==2 or featureSel==2: #maxMean
				if mean_X>feature:
					feature=mean_X
					repProbe=probe
			elif method==3 or featureSel==3: #maxStddev
				if stddev_X>feature:
					feature=stddev_X
					repProbe=probe
			elif method==4 or featureSel==4:	#minStddev
				if stddev_X<feature:
					feature=stddev_X
					repProbe=probe
				
		#print >> sys.stderr, "feature=",feature	
		if feature<minFilter or feature>maxFilter:
			continue;

		
		print >> sys.stdout, OFS.join(getIncludedCols(repProbe,includes))


def usage():
	print >>sys.stderr, "Usage:",sys.argv[0],"[options] fileName[-:stdin] idCol1[a-b,c,...] startRow valueCol1[a-b,c,...]";
	print >> sys.stderr,"options"
	print >> sys.stderr,"--method method\tSpecify the method:"
	print >> sys.stderr,"\tparadigm probe method: maxMax, maxMean, maxStddev, minStdddev"
	print >> sys.stderr,"\t\trepresent a whole proset by a paradigm probe chosen by any of the criteria: maxMax: probe containing highest intensity value; maxMean: probe with highest mean over samples; maxStddev,minStddev: probes with highest, lowest intensity variation, respectively"
	print >> sys.stderr,"\tvertically collapsed metaprobe: meanProbes, medianProbes, meanProbesRO, >> medianProbesRO <<, maxProbes"
	print >> sys.stderr,"\t\t\tcollapse probe values vertical into a pseudo probes by mean or median"
	print >> sys.stderr,"\t\t\tRO=to remove outlier"
	print >> sys.stderr,"--feature f: mean, max, stddev: features to use in filter"
	print >> sys.stderr,"--minFilter x\tTo filter minimum"
	print >> sys.stderr,"--maxFilter x\tTo filter maximum"
	print >> sys.stderr,"--specialCols method:idCol1[a-b,c,...]:params:...\tTo collapse these columns by a special method: medianProbes, meanProbes,medianProbesRO ,meanProbesRO, percentile:idCol1:p (0.0=min,1.0=max), countIfInRangeInc:idCol1:L:H , countIf:idCol1:x:..., countIff:idCol1:f:..."
	print >> sys.stderr,"--sep t\tinput and output separator"
	print >> sys.stderr,"--fs t\tinput separator [TAB]"
	print >> sys.stderr,"--ofs t\toutput seperator [TAB]"
	print >> sys.stderr,"--headerRow n\tset header row. [default is 1]"
	print >> sys.stderr,"--scm method:param:.. --scc cols --mcs"
	print >> sys.stderr,"--includesOnlyMentioned, --iom"
	print >> sys.stderr,"--includes cols"
	print >> sys.stderr,"--excludes cols"
	print >> sys.stderr,"--suppressStrFloatErrorAbortion. Don't abort on str float conversion error"
	print >> sys.stderr,"--suppressStrFloatErrorReturnValue defaultValueOnError"
	explainColumns(sys.stderr)

	

def main():
	Methods={"maxMax":1,"maxMean":2,"maxStddev":3,"minStddev":4,"meanProbes":5,"medianProbes":6,"meanProbesRO":7,"medianProbesRO":8,
 "max":1,"mean":2,"stddev":3,"percentile":9,"countIfInRangeInc":10,"countIf":11,"min":12,"countIff":13,"minRO":14,"maxRO":15,"percentileRO":16,"medianRO":8,"maxProbes":17}
	global suppressStrFloatErrorAbortion
	global exceptionFloatDefaultValue

	method=Methods["medianProbesRO"]
	feature=-1
	headerRow=1

	scmMethod=-1
	scmParams=[]
	sccTmp=[]

	includeCmd=[]
	includeOnlyMentioned=False
	includes=[]

	minFilter=float(MIN_INT)
	maxFilter=float(MAX_INT)
	
	fs="\t"
	ofs="\t"
	specialColOpsTmp=[]
	specialColOps=dict()

	optlist,args=getopt(sys.argv[1:],'',["method=","minFilter=","maxFilter=","feature=","specialCols=","sep=","fs=","ofs=","headerRow=","scm=","scc=","mcs","includes=","excludes=","includesOnlyMentioned","iom","suppressStrFloatErrorAbortion","suppressStrFloatErrorReturnValue="])

	suppressStrFloatErrorAbortion=False

	if len(args)<4:
		usage()
		return
	
	try:
		for opt,val in optlist:
			if opt=="--method":
				try:
					method=Methods[val]
				except KeyError:
					print >> sys.stderr,"Unknown Method:",val
			elif opt=="--minFilter":
				minFilter=float(val)
			elif opt=="--maxFilter":
				maxFilter=float(val)
			elif opt=="--feature":
				try:
					feature=Methods[val]
				except KeyError:
					print >> sys.stderr,"Unknown Filtering Feature:",val
			elif opt=="--specialCols":
				parseMethod=val.split(":")
				try:
					met=Methods[parseMethod[0]]
					
					params=[]
					if len(parseMethod)>1:
						params=parseMethod[1:]  ##2->1
					
					if met==12: #min
						specialOp=[Methods["percentile"],[0.0]]
					elif met==1: #max
						specialOp=[Methods["percentile"],[1.0]]
					elif met==14: #minRO
						specialOp=[Methods["percentileRO"],[0.0]]
					elif met==15: #maxRO
						specialOp=[Methods["percentileRO"],[1.0]]
					else:
						specialOp=[met,params]
					
					specialColOpsTmp.append([parseMethod[1],specialOp])
					
				except:
					print >> sys.stderr,"Error understanding special Cols:",val
		
			elif opt=="--scm":
				parseMethod=val.split(":")
				try:
					met=Methods[parseMethod[0]]
					params=parseMethod[1:]

					if met==12: #min
						specialOp=[Methods["percentile"],[0.0]]
					elif met==1: #max
						specialOp=[Methods["percentile"],[1.0]]
					elif met==14: #minRO
						specialOp=[Methods["percentileRO"],[0.0]]
					elif met==15: #maxRO
						specialOp=[Methods["percentileRO"],[1.0]]
					else:
						specialOp=[met,params]
					
					
				except:
					print >> sys.stderr,"Error understanding special Cols:",val
			elif opt=="--scc":
				sccTmp.append(val)
			elif opt=="--mcs":
				#now add!
				for scct in sccTmp:
					specialColOpsTmp.append([scct,specialOp])			
			elif opt=="--sep":
				fs=replaceSpecialChar(val)
				ofs=fs
			elif opt=="--fs":
				fs=replaceSpecialChar(val)
			elif opt=="--ofs":
				ofs=replaceSpecialChar(val)
			elif opt=="--headerRow":
				headerRow=int(val)
			elif opt in ["--includesOnlyMentioned","--iom"]:
				includeOnlyMentioned=True
			elif opt=="--includes":
				includeCmd.append([1,val])
			elif opt=="--excludes":
				includeCmd.append([0,val])
			elif opt=="--suppressStrFloatErrorAbortion":
				suppressStrFloatErrorAbortion=True	
			elif opt=="--suppressStrFloatErrorReturnValue":
				suppressStrFloatErrorAbortion=True
				exceptionFloatDefaultValue=float(val)
				


	except GetoptError, err:
		print err
		usage()
		return

	if feature==-1:
		if method in [1,2,3,4]:
			feature=method
		else:
			feature=1	

	if method in [1,2,3,4] and feature!=method:
		print >> sys.stderr,"Conflicting feature and method: set feature=method"
		feature=method
				
	if method not in [5,6,7,8] and len(specialColOps.keys())>0:
		print >> sys.stderr,"conflicting method: special cols ignored, method=",method,"specialColOp=",specialColOps

	fileName=args[0]

	startRow=int(args[2])

	
	if headerRow>startRow:
		print >> sys.stderr,"Error: header row must not be after start row!"
		return	

	geneSets=dict();

		
	header,prestarts=getHeader(fileName,headerRow,startRow,fs)
	

	
	for i in range(0,len(header)):
		if includeOnlyMentioned==True:
			includes.append(0)
		else:	
			includes.append(1)	
		
	idCols=getCol0ListFromCol1ListStringAdv(header,args[1])	
	for col in idCols:
		includes[col]=1
	print >> sys.stderr,"idCols0=",getIncludesColsByIndexVector(header,idCols)

	lineOrderedKey=getGeneSets(geneSets,fileName,idCols,startRow,fs)
	
	valueCols=getCol0ListFromCol1ListStringAdv(header,args[3])
	for col in valueCols:
		includes[col]=1

	print >> sys.stderr,"valCols0=",getIncludesColsByIndexVector(header,valueCols)

	for colString,methodOp in specialColOpsTmp:
		cols0=getCol0ListFromCol1ListStringAdv(header,colString)
		
		print >> sys.stderr,"apply",methodOp,"on",cols0	
		for col0 in cols0:
			#print >> sys.stderr,col0,methodOp
			specialColOps[col0]=methodOp
			includes[col0]=1
	
	for includeFlag,colString in includeCmd:
		cols0=getCol0ListFromCol1ListStringAdv(header,colString)
		print >> sys.stderr,"i/e",includeFlag,getIncludesColsByIndexVector(header,cols0)
		for col0 in cols0:
			includes[col0]=includeFlag

	print >> sys.stderr,"output fields:"
	
	i0=0
	orig0=-1
	for inc in includes:
		orig0+=1		
		if inc==1:
			print >> sys.stderr, str(i0+1)+"\t"+excelColIndex(i0)+"\t"+header[orig0]
			i0+=1	

	for prestartrow in prestarts:
		print >> sys.stdout,ofs.join(getIncludedCols(prestartrow,includes))

	collapseProbes(geneSets,lineOrderedKey,idCols,valueCols,minFilter,maxFilter,method,feature,specialColOps,fs,ofs,includes);

main();
