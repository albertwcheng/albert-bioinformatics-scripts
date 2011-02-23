#!/usr/bin/python

from sys import stderr
from sys import stdout
from sys import argv
from glob import glob
from os.path import basename

"""

readlength 6
chr3	150	155	-

"""

def sortExplace(L):
	try:
		return sorted(L)
	except NameError:
		Lprime=L[:]
		Lprime.sort()
		return Lprime

def BED2YoungLabFormat(filename,ofilename):
	fin=open(filename)
	
	readInfo=dict()
	
	#store read info into [mismatch][chr][]=coord	
	for line in fin:
		fields=line.rstrip().split("\t")	
		chrom=fields[0].strip()
		
		if chrom[:3]=='chr':
			chrom=chrom[3:]

		
		
		strand=fields[3]

		position=int(fields[1])
		
		endposition=int(fields[2])
		tra=endposition-position
		mismatch=0
		
		if strand=='-':
			position=-(position+tra)
		
		try:
			mismatchSlot=readInfo[mismatch]
		except KeyError:
			mismatchSlot=dict()
			readInfo[mismatch]=mismatchSlot
		
		try:
			chrSlot=mismatchSlot[chrom]
		except KeyError:
			chrSlot=[]
			mismatchSlot[chrom]=chrSlot
		
		chrSlot.append(position)
	
	
	fin.close()
	
	fout=open(ofilename,'w')
	
	for mismatch in sortExplace(readInfo.keys()):
		mismatchSlot=readInfo[mismatch]
		mismatchKey="#U"+str(mismatch)
		fout.write(mismatchKey+"\n")
		for chrom in sortExplace(mismatchSlot.keys()):
			fout.write(">"+chrom+"\n")
			chrSlot=mismatchSlot[chrom]
			chrSlot.sort()
			for position in chrSlot:
				fout.write(str(position)+"\n")
	
	fout.close()

def changeExtension(prefix,filename,removeOrigExtension,newsuffix):
	bnfile=basename(filename)
	fncomp=bnfile.split(".")
	lfncomp=len(fncomp)
	if lfncomp > 1 and removeOrigExtension:
		del fncomp[lfncomp-1]
		
	fncomp.append(newsuffix)
	return prefix+"/"+(".".join(fncomp))

def BED2YoungLabFormat_Main(fileList,outPrefix,newSuffix):
	print >> stderr, "Convert bedfiles",fileList,"to young lab files"
	for file in fileList:
		
		ofile=changeExtension(outPrefix,file,True,newSuffix)	
		print >> stderr,file,">>",ofile
		BED2YoungLabFormat(file,ofile)
	
	print >> stderr, "<Done>"
	
	


largv=len(argv)
if largv<4:
	print >> stderr,argv[0],"srcFiles outputFolder newextesion"
else:
	BED2YoungLabFormat_Main(argv[1:largv-2],argv[largv-2],argv[largv-1])