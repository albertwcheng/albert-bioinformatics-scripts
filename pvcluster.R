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
#This is based on tutorial from Steven M. Holland
#http://www.uga.edu/strata/software/pdf/pcaTutorial.pdfJOawJ5IyJuS3Hg&cad=rja
#
#
###################################################################################


args <- commandArgs(TRUE)


largs <- length(args)


if(largs<2){
	cat("Usage: \n\t[Rscript] pvcluster.R filename jobname\n")
	quit()	
}


filename=args[1]
jobname=args[2]

library(pvclust)

sink()

rankPerColumn <- function(matrix,start=1,end=-1)
{
	dimension=dim(matrix)	
	nCols=dimension[2]
	if(end<1)
	{
		end=nCols	
	}
	for(i in start:end)
	{
		matrix[,i]=rank(matrix[,i])
	}
	
	return (matrix)
}

startpng <- function(desc)
{
	
	print(desc,quote=FALSE)
	filename=paste("./",paste(strsplit(desc," ")[[1]],collapse="_",sep=""),"_pvclust.png",sep="")
	filenameSink=paste("./",paste(strsplit(desc," ")[[1]],collapse="_",sep=""),"_pvclust.txt",sep="")	
	print(paste("write image to",filename,sep=" "),quote=FALSE)
	print(paste("write table to",filenameSink,sep=" "),quote=FALSE)
	
	return(c(filename,filenameSink))
	
}

endpng <- function(filename,x)
{
	png(filename[1],h=600,w=800)	
	plot(x)
	dev.off()
	sink(filename[2])
	print(x)

	sink()
}


data=read.delim(filename) 



valcolumns=2:dim(data)[2]

data.allProbes=data[,valcolumns]
rank.allProbes=rankPerColumn(data.allProbes)

dir.create(jobname)
setwd(jobname)

filenameSink =startpng("allprobes spearman average")
cluster.allProbes.spearman.average =pvclust(rank.allProbes,method.dist="cor",method.hclust="average")
endpng(filenameSink,cluster.allProbes.spearman.average)

filenameSink =startpng("allprobes spearman complete")
cluster.allProbes.spearman.complete =pvclust(rank.allProbes,method.dist="cor",method.hclust="complete")
endpng(filenameSink,cluster.allProbes.spearman.complete)

filenameSink =startpng("allprobes pearson average")
cluster.allProbes.spearman.average =pvclust(data.allProbes,method.dist="cor",method.hclust="average")
endpng(filenameSink,cluster.allProbes.spearman.average)

filenameSink =startpng("allprobes pearson complete")
cluster.allProbes.spearman.complete =pvclust(data.allProbes,method.dist="cor",method.hclust="complete")
endpng(filenameSink,cluster.allProbes.spearman.complete)

