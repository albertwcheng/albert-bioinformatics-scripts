#!/usr/bin/env Rscript

###################################################################################
#Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
#
#
#
###################################################################################


library(mwt)

splitString <- function(str,sep)
{
	
	return( unlist(strsplit(str,sep))	)
}

args=commandArgs(TRUE)

#skipArgsUntilNoOptions <- function(args)
#{
#	lastOption=1
#	
#	largs=length(args)
#
#	for(i in 1:length(args))
#	{
#		if(substr(args[i],1,2)=="--")
#		{
#			lastOption=i	
#		}
#	}
#
#	return(args[(lastOption+1):largs])
#}
#
#args=skipArgsUntilNoOptions(args)

if(length(args)<5)
{
	cat(paste("usage:","MWTAnalysis.R","filename grpvector[sep by , 0=group1 or 1=group2, NA means ignore] logitForMWT[1,0] [ratio|diff] group1Prefix group2Prefix comparisonPrefix outfilename\n"))
	cat("you can get the simple matrix and the mwt grp file by running prepareGSEAFiles.sh and getting the content of *.mwtcls for the grp arg\n")
	quit()
}

filename=args[1]
grpvector=args[2]
logit=as.integer(args[3])
differential=args[4]
group1Prefix=args[5]
group2Prefix=args[6]
comparisonPrefix=args[7]
outfilename=args[8]

cat("filename"); cat(filename); cat("\n");

data.raw=read.delim(filename)
#split off group vector

numRows=dim(data.raw)[1]
numCols=dim(data.raw)[2]
cat(paste("input file ",filename," has ",numCols," columns"))


MWTOnSubMatrix <- function(matrix,grp,log.it=FALSE)
{
	toInclude=!is.na(grp)
	matrixInclude=as.matrix(matrix[,toInclude])
	grp.noNA=grp[toInclude]
	print(grp.noNA)
	print(matrixInclude[1:min(5,numRows),])
	return(mwt(matrixInclude,grp.noNA,log.it))
}

DiffOnSubMatrix <- function(matrix,grp)
{
	group1=(grp==0 & !is.na(grp))
	group2=(grp==1 & !is.na(grp))
	group1data=as.matrix(matrix[,group1])
	group2data=as.matrix(matrix[,group2])
	group1dataRowMeans=rowMeans(group1data)
	group2dataRowMeans=rowMeans(group2data)
	dif=group2dataRowMeans-group1dataRowMeans
	mat=cbind(group1dataRowMeans,group2dataRowMeans,dif)
	colnames(mat)=c("$$1$MEAN","$$2$MEAN","$$$DIFF")
	return(mat)
}

RatioOnSubMatrix <- function(matrix,grp)
{
	group1=(grp==0 & !is.na(grp))
	group2=(grp==1 & !is.na(grp))
	group1data=as.matrix(matrix[,group1])
	group2data=as.matrix(matrix[,group2])
	group1dataRowMeans=rowMeans(group1data)
	group2dataRowMeans=rowMeans(group2data)
	rat=group2dataRowMeans/group1dataRowMeans
	mat=cbind(group1dataRowMeans,group2dataRowMeans,rat)
	colnames(mat)=c("$$1$MEAN","$$2$MEAN","$$$RATIO")
	return(mat)
}

mwt.input=data.raw #use all columns   #data.raw[,2:numCols] #first column is always excluded

grp=as.integer(splitString(grpvector,","))
mwt=MWTOnSubMatrix(mwt.input,grp,(logit==1))

if(differential=="ratio")
{
	rats=RatioOnSubMatrix(mwt.input,grp)
	dataOutput=cbind(data.raw,rats,"$$$MWT"=mwt$MWT,"$$$FDR"=mwt$FDR)
	
} else {
	dif=DiffOnSubMatrix(mwt.input,grp)
	dataOutput=cbind(data.raw,dif,"$$$MWT"=mwt$MWT,"$$$FDR"=mwt$FDR)
	
}

colnams=colnames(dataOutput)

for(i in 1:length(colnams))
{
	if(colnams[i]=="$$1$MEAN")
	{
		colnams[i]=paste(group1Prefix,"mean",sep=".")	
	}
	if(colnams[i]=="$$2$MEAN")
	{
		colnams[i]=paste(group2Prefix,"mean",sep=".")	
	}
	if(colnams[i]=="$$$RATIO")
	{
		colnams[i]=paste(comparisonPrefix,"ratio",sep=".")	
	}
	if(colnams[i]=="$$$DIFF")
	{
		colnams[i]=paste(comparisonPrefix,"diff",sep=".")	
	}		
	if(colnams[i]=="$$$MWT")
	{
		colnams[i]=paste(comparisonPrefix,"MWT",sep=".")	
	}		
	if(colnams[i]=="$$$FDR")
	{
		colnams[i]=paste(comparisonPrefix,"FDR",sep=".")	
	}		
}

colnames(dataOutput)=colnams


write.table(dataOutput,file=outfilename,quote=FALSE,sep="\t",row.names=FALSE)