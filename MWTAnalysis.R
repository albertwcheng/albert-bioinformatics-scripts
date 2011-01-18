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

args=commandArgs()

if(length(args)<7)
{
	print(paste("usage:",args[1],"--vanilla filename labelprefix grpvector[sep by , 1 or 0, NA means ignore] logit[1,0] outfilename"))
	quit()
}

filename=args[3]
labelprefix=args[4]
grpvector=args[5]
logit=as.integer(args[6])
outfilename=args[7]

data.raw=read.delim(filename)
#split off group vector

numRows=dim(data.raw)[1]
numCols=dim(data.raw)[2]
print(paste("input file ",filename," has ",numCols," columns"))


MWTOnSubMatrix <- function(matrix,grp,log.it=FALSE)
{
	toInclude=!is.na(grp)
	matrixInclude=as.matrix(matrix[,toInclude])
	grp.noNA=grp[toInclude]
	print(grp.noNA)
	print(matrixInclude[1:min(5,numRows),])
	return(mwt(matrixInclude,grp.noNA,log.it))
}

mwt.input=data.raw #use all columns   #data.raw[,2:numCols] #first column is always excluded

grp=as.integer(splitString(grpvector,","))
mwt=MWTOnSubMatrix(mwt.input,grp,(logit==1))

write.table(cbind(data.raw,MWT=mwt$MWT,FDR=mwt$FDR),file=outfilename,quote=FALSE,sep="\t",row.names=FALSE)