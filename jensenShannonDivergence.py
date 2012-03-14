#!/usr/bin/env python

from getopt import getopt
from albertcommon import *
from sys import *
from math import log,fsum

''' This part is copied from https://bitbucket.org/cevans/bootstrap/src/0f6e0b8c8a26/scikits/bootstrap/bootstrap.py not used yet

from numpy.random import randint
from scipy.stats import norm
from numpy import *

def ci(data,statfun,alpha=0.05,n_samples=10000,method='bca'):
        """..."""

        # Ensure that our data is, in fact, an array.
        data = array(data)

        # First create array of bootstrap sample indexes:
        indexes = randint(data.shape[0],size=(n_samples,data.shape[0]))

        # Then apply this to get the bootstrap samples and statistics over them.
        samples = data[indexes]

        stat = array([statfun(x) for x in samples])
        
        # Normal-theory Interval --- doesn't use sorted statistics.
        if method == 'nti':
                bstd = std(stat)
                pass
        
        stat_sorted = sort(stat)
        
        # Percentile Interval
        if method == 'pi':
                return ( stat_sorted[round(n_samples*alpha/2)], stat_sorted[round(n_samples*(1-alpha/2))] )

        # Bias-Corrected Accelerated Interval
        elif method == 'bca':
                ostat = statfun(data)

                z = norm.ppf( ( 1.0*sum(stat < ostat) + 0.5*sum(stat == ostat) ) / n_samples )
                
                # Calculate the jackknife distribution and corresponding statistics quickly.
                j_indexes = (lambda n: delete(tile(array(range(0,n)),n),range(0,n*n,n+1)).reshape((n,n-1)))(len(data))
                jstat = [statfun(x) for x in data[j_indexes]]
                jmean = mean(jstat)

                a = sum( (jstat - jmean)**3 ) / ( 6.0 * sum( (jstat - jmean)**2 )**1.5 )

                zp = z + norm.ppf(1-alpha/2)
                zm = z - norm.ppf(1-alpha/2)

                a1 = norm.cdf(z + zm/(1-a*zm))
                a2 = norm.cdf(z + zp/(1-a*zp))

                return (stat_sorted[round(n_samples*a1)],stat_sorted[round(n_samples*a2)])

        else:
                raise "Method %s not supported" % method
'''

#sigma over i (weighti * Pi)
def sumProbDists(PM,weights):

	lenFirstPM=len(PM[0])
	
	for P in PM:
		if len(P)!=lenFirstPM:
			print >> stderr,"error: length of P's in PM not consistent. Abort"
			exit(1)
	
	summedP=[]
	for i in range(0,lenFirstPM):
		summed=0.0
		for w,P in zip(weights,PM):
			summed+=w*P[i]
		summedP.append(summed)
	
	return summedP
	
#logb=log(base)
def shannonEntropy(P,logb):
	E=0.0
	for p in P:
		if p<0:
			print >> stderr,"error: negative probability. Abort"
			exit(1)
		#if p==0: no need to do anything, ignore..	
		if p>0:
			E-=p*log(p) #in natural log

	return E/logb #in proper base


def kullBackLeiblerDivergence(P,Q,logb):
	d=0.0
	for p,q in zip(P,Q):
		if p>0:
			d+=p*(log(p)-log(q))  #in natural log
	
	return d/logb #in proper base
	

def JSDTwoP(P,Q,logb):
	M=sumProbDists([P,Q],[0.5,0.5])
	return (kullBackLeiblerDivergence(P,M,logb)+kullBackLeiblerDivergence(Q,M,logb))/2
	
def JSD(PM,weights,logb):
	M=sumProbDists(PM,weights)
	firstTerm=shannonEntropy(M,logb)
	secondTerm=0.0
	for w,P in zip(weights,PM):
		secondTerm+=w*shannonEntropy(P,logb)

	return firstTerm-secondTerm
	




def testTwoPCaseAndExit():
	P=[0.5,0.3,0.2]
	Q=[0.2,0.7,0.1]
	
	logb=log(2)
	
	print >> stderr,"JSDTwoP=",JSDTwoP(P,Q,logb)
	print >> stderr,"JSD=",JSD([P,Q],[0.5,0.5],logb)
	
	
	exit(0)

#groupInfo will become [ [groupName,cols,weight,actualColsIdx,PM] ]
def readFilePMsIntoGroupInfo(filename,groupInfo):
	startRow=2
	headerRow=1
	fs="\t"
	
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	for groupI in range(0,len(groupInfo)):
		groupName,cols,weight=groupInfo[groupI]
		actualColsIdx=getCol0ListFromCol1ListStringAdv(header,cols)
		groupInfo[groupI].append(actualColsIdx)
		PM=[]
		#now init PM according to the number of cols
		for i in range(0,len(actualColsIdx)):
			PM.append([]) #empty Prob dist for appending later while reading file
			
		groupInfo[groupI].append(PM)
	
	#now read file
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue
		
		lin=lin.rstrip("\r\n")
		if len(lin)<1:
			continue #no content on this row, skip
		
		fields=lin.split(fs)
		#now assume first col is geneName
		geneName=fields[0]
		
		#now go to each groupInfo, and append appropriate PMs
		for groupName,cols,weights,actualColsIdx,PM in groupInfo:
			thisAppend=[]
			hasNA=False
			for colIdx in actualColsIdx:
				try:
					thisValue=float(fields[colIdx])
					thisAppend.append(thisValue)
				except:
					#invalid value skip the whole row
					hasNA=True
					break
					
			if hasNA:
				print >> stderr,"line",lino,"with rowName",geneName,"for group",groupName,"discarded due to invalid value"
			else:
				#now we can append, grow each P in PM for one entry
				for P,appendee in zip(PM,thisAppend):
					P.append(appendee)
			
	fil.close()

class NegativeProbabilityError:
	pass

#normalize element in P such that it sums to 1	
def normalizeP(P):
	#negative values? renormalize P such that all values are >=0
	minP=min(P)
	if minP<0:
		for i in range(0,len(P)):
			P[i]-=minP
			
	PSum=float(fsum(P))
	for i in range(0,len(P)):
		if P[i]<0:
			#should abort instead!!
			print >> stderr,"negative prob, abort"
			exit(1)
			#raise ZeroDivisionError
		P[i]/=PSum
	

def percentileCI(stats,alpha):
	n_samples=len(stats)
	stat_sorted=sorted(stats)
	return ( stat_sorted[int(round(n_samples*alpha/2))], stat_sorted[int(round(n_samples*(1-alpha/2)))] )

def bootstrap(PM,weights):
	PMp=[]
	weightsp=[]
	N=len(PM)
	
	for i in range(0,N):
		choice=randint(0,N-1)
		PMp.append(PM[choice])
		weightsp.append(weights[choice])
	
	#now normalize weightsp
	normalizeP(weightsp)
	return PMp,weightsp


def printUsageAndExit(programName):
	print >> stderr,programName,"[options] infile [[groupName cols weight] ...]"
	print >> stderr,"weight=1/n to let the program to calculate the weight evenly or use comma separated list"
	print >> stderr,"Options:"
	print >> stderr,"--logbase x. default 2, i.e., in bits"
	print >> stderr,"--readGroupFile filename. read group def in file as rows of tab-delimited groupName cols weight"
	print >> stderr,"--removeAllZeroSamples. Remove all zero samples and samples containing negative values. If not set, for samples that all-zero or has negative values, program will abort."
	print >> stderr,"--bootstrapTrials x. default 10000."
	print >> stderr,"--cialpha x. default 0.05. Set alpha for bootstrap CI"
	exit(1)


			
if __name__=="__main__":

	#testTwoPCaseAndExit()
	


	programName=argv[0]
	opts,args=getopt(argv[1:],'',['logbase=','readGroupFile=','removeAllZeroSamples','bootstrapTrials=','cialpha='])
	
	bootstrapTrials=10000
	logb=log(2)
	readGroupFile=None
	removeAllZeroSamples=False
	cialpha=0.05
	
	for a,v in opts:
		if a=='--logbase':
			logb=log(float(v))
		elif a=='--readGroupFile':
			readGroupFile=v
		elif a=='--removeAllZeroSamples':
			removeAllZeroSamples=True
		elif a=='--bootstrapTrials':
			bootstrapTrials=int(v)
		elif a=='--cialpha':
			cialpha=float(v)
			
				
	evenWeight=False
	
	unprocessedGroupInfo=[]
	
	groupInfo=[]
	
	if readGroupFile:
		fil=open(readGroupFile)
		for lin in fil:
			unprocessedGroupInfo.append(lin.rstrip("\r\n").split("\t"))
		fil.close()		
	
	try:
		infile=args[0]
	except:
		printUsageAndExit(programName)
		
	if (len(args)-1)%3!=0:
		print >> stderr,"invalid number of arguments. Abort"
		printUsageAndExit(programName)
	
	for i in range(1,len(args),3):
		unprocessedGroupInfo.append(args[i:i+3])
	
	for unprocessedGroupInfoEntry in unprocessedGroupInfo:
		groupName,cols,weight=unprocessedGroupInfoEntry
		
		
		
		if weight=="1/n":
			weight=None
		else:
			weight=weight.split(",")
			for i in range(0,len(weight)):
				weight=float(weight)
				#ensure weight sums to 1, normalize it.
			
		
		groupInfo.append([groupName,cols,weight])
		
	

	
	#read file into PM
	readFilePMsIntoGroupInfo(infile,groupInfo)

	#numGroup=len(groupInfo)

	
	#now normalize PMs
	for thisGroupInfo in groupInfo:
	
		
		groupName,cols,weight,actualColIdx,PM=thisGroupInfo
		for i in range(len(PM)-1,-1,-1): #from end.
			P=PM[i]
			try:
				normalizeP(P)
			except ZeroDivisionError:
				#all zeros!!?!
				if removeAllZeroSamples:
					#remove this P and the weight and from the actualColIdx
					del actualColIdx[i]
					del PM[i]
					if weight:
						del weight[i]
				else:
					print >> stderr,"contains all-zero sample. Abort unless --removeAllZeroSamples specified"
					printUsageAndExit(programName)
				
		
		if not weight: #not specified, depends on the number of samples in group, set even weight
			numSamples=len(PM)
			weight=[1.0/numSamples]*numSamples
			thisGroupInfo[2]=weight
		
		normalizeP(weight)	#redistribute weight to make sure it sums to one (in case incorrect inputs or changes made above
			
	#now it's ready for the math
	#for each group compute JSDivergence and output
	print >> stdout,"\t".join(["GroupName","ColSelector","ColAnalyzed","NumColAnalyzed","Weights","JSD","JSDNegError","JSDPosError","BootstrapCIMin","BootstrapCIMax","BootstrapJSDMin","BootstrapJSDMax"])
	
	
	for groupName,cols,weights,actualColsIdx,PM in groupInfo:
		print >> stderr,"Calculating JSD for group",groupName,"..."
		jsd=JSD(PM,weights,logb)
		bstrpJSD=[]
		#now print
		for T in range(0,bootstrapTrials):
			if T%1000==0:
				print >> stderr,"\tWorking on bootstrap %d of %d" %(T+1,bootstrapTrials)
			PMp,weightsp=bootstrap(PM,weights)
			bstrpJSD.append(JSD(PMp,weightsp,logb))
			
		CI=percentileCI(bstrpJSD,cialpha)
		print >> stdout,"\t".join([groupName,cols,",".join(toStrList(actualColsIdx)),str(len(actualColsIdx)),",".join(toStrList(weights)),str(jsd),str(jsd-CI[0]),str(CI[1]-jsd),str(CI[0]),str(CI[1]),str(min(bstrpJSD)),str(max(bstrpJSD))])
	
	
	#print >> stderr,"<Done>"