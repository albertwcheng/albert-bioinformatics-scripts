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
# Uses library pcaMethods
#
#
###################################################################################


library(pcaMethods)

args <- commandArgs(TRUE)


largs <- length(args)

if(largs<3){
	cat("Usage: \n\t[Rscript] PCAMVE.R matrixFileName outFilledMatrixFileName method[ppca,bpca,nipals,svdImpute]\n")
	cat("\nDescriptions:\n")
	cat("\tPerform missing value estimation using pcaMethods, bpca, ppca, etc\n")
	quit()	
}


separator="\t"

matrixFileName=args[1]
outputName=args[2]
method=args[3]


#read data and print first 5 lines
mydata <- read.table(file=matrixFileName,header=TRUE,row.names=1,sep=separator) 

result <- pca(mydata, method=method, nPcs=2, center=FALSE)

cat("X\t",file=outputName)
write.table(result@completeObs,file=outputName,sep="\t",quote=FALSE,append=TRUE)