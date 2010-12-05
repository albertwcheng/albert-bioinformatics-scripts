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
	cat("Usage: \n\t[Rscript] PCAforMatrix.R matrixFileName outputDir [center:yes] [scale:yes] [sep:tab] [showMaxPC:20] [ [drawcomponents:1,2] ...]\n")
	cat("\nDescriptions:\n")
	cat("\tPerform PCA analysis on a matrix file where data vectors are in rows. For data vectors in columns, first perform transposition, e.g., by using matrixTranspose.py originalMatrix > transposedMatrix. Output to outputDir\n")
	cat("\nOptions Descriptions:\n")
	cat("\tcenter\t\t\t\tWhether to set mean to 0\n")
	cat("\tscale\t\t\t\tWhether to scale such that sd=1 for each data vector\n")
	cat("\tsep\t\t\t\tSet field separator\n")
	cat("\tshowMaxPC\t\t\tHow many maximum PC to plots on variance plots\n")
	cat("\tdrawcomponents...\t\tSpecify PC pairs to draw the PCA plot, biplot and loading plot. By default 1 and 2 are already included. e.g., 2,3 4,5 will draw PCA1,2 PCA2,3 and PCA4,5\n")
	cat("\nOutput Descriptions (in outputDir):\n")
	cat("\tloading.txt\t\t\tThe loading matrix for the variables and PCs\n")
	cat("\tscores.txt\t\t\tThe PCA score matrix\n")
	cat("\tsd.txt\t\t\t\tThe singular values, variances info\n")
	cat("\tsummary.txt\t\t\tThe summary report from R on the pca result object\n")
	cat("\tloading.<c1>,<c2>.png\t\tThe loading plot for components <c1> and <c2>\n")
	cat("\tPCA.<c1>,<c2>.png\t\tThe PCA score plot for components <c1> and <c2>\n")
	cat("\tPCABiPlot.<c1>,<c2>.png\t\tThe Biplot for components <c1> and <c2>\n")
	quit()	
}


center="yes"
scale="yes"
separator="\t"
matrixFileName=args[1]
outputDir=args[2]
showMaxPC=20
drawcomponents=cbind(c(0,0),c(1,2))

if(largs>=3){
	center=args[3]
	if(largs>=4){
		scale=args[4]
		if(largs>=5)
		{
			separator=args[5]
			
			
			if(largs>=6)
			{
				showMaxPC=as.numeric(args[6])
				
				if(largs>=7){
					for(i in 7:largs){
						fields=as.numeric(unlist(strsplit(args[i],",")))
						drawcomponents=cbind(drawcomponents,fields)					}
				}
				
			}
		}
	}	
}

if(separator=="\\t")
{
	separator="\t"
}

#print(drawcomponents)
#quit()

centerFlag=(center=="yes")
scaleFlag=(scale=="yes")

#read data and print first 5 lines
mydata <- read.table(file=matrixFileName,header=TRUE,row.names=1,sep=separator) #,colClasses=c("character","double","double")


mydata.pca <- prcomp(mydata,scale.=scaleFlag, retx=TRUE, center=centerFlag) 
#variable means set to zero, and variances set to one
#sample scores stored in mydata.pca$x
#loadings stored in mydata.pca$rotation
#singular values (square roots of eigenvalues) stored in mydata.pca$sdev  (standard deviation explained by each PC)
#variable means stored in mydata.pca$center
#variable standard deviations stored in mydata.pca$scale

sd <- mydata.pca$sdev #this is the singular values=stdev (square roots of eigenvalues=variances) explained by each PC
variances=sd^2
loadings <- mydata.pca$rotation #these are the weights in cols (the eigenvectors) indexed by the PC component index
rownames(loadings) <- colnames(mydata) #the names of the genes and the corresponding loadings, i.e., weights on the rows of the loadings matrix (eigenvectors)
scores <- mydata.pca$x #these are the new data in the PC coordinate systems

if(!file.exists(outputDir)){
	dir.create(outputDir) #create output directory
}


sink(paste(outputDir,"/","summary.txt",sep=""))
cat("First 5 lines of Data:\n")
print(mydata[1:min(5,dim(mydata)[1]),])
cat("\nCenter:\n")
print(mydata.pca$center)
cat("\n")
summary(mydata.pca)
#cat("\nloadings:\n")
#print(loadings)
#cat("\nsingular values:\n")
#cat(sd)
#cat("\n\nscores:\n")
#print(scores)
sink()


#now plots
#print(ncol(drawcomponents))

for(prequestI in 2:ncol(drawcomponents)){
	compv=drawcomponents[,prequestI]
	#print(compv)
	c1=compv[1]
	c2=compv[2]
	cat("Drawing plots for","PCA",c1,"and","PCA",c2,"\n")	
	png(filename=paste(outputDir,"/","PCABiPlot.",c1,",",c2,".png",sep=""))
	biplot(scores[,c(c1,c2)],loadings[,c(c1,c2)],xlab=paste("PCA",c1),ylab=paste("PCA",c2),cex=0.7)
	abline(h=0,lty=2)
	abline(v=0,lty=2)
	sink("/dev/null")
	dev.off()
	sink()

	png(filename=paste(outputDir,"/","PCA.",c1,",",c2,".png",sep=""))
	minV=min(scores[,c(c1,c2)])
	maxV=max(scores[,c(c1,c2)])
	plot(scores[,c1],scores[,c2],xlab=paste("PCA",c1),ylab=paste("PCA",c2),type="n",xlim=c(minV,maxV),ylim=c(minV,maxV))
	text(scores[,c1],scores[,c2],rownames(scores),col="blue",cex=0.7)
	abline(h=0,lty=2)
	abline(v=0,lty=2)
	sink("/dev/null")
	dev.off()
	sink()

	png(filename=paste(outputDir,"/","loading.",c1,",",c2,".png",sep=""))
	minL=min(loadings[,c(c1,c2)])
	maxL=max(loadings[,c(c1,c2)])
	plot(loadings[,c1],loadings[,c2],xlab=paste("PCA",c1),ylab=paste("PCA",c2),type="n",xlim=c(minL,maxL),ylim=c(minL,maxL))
	text(loadings[,c1],loadings[,c2],rownames(loadings),col="blue",cex=0.7)
	abline(h=0,lty=2)
	abline(v=0,lty=2)
	sink("/dev/null")
	dev.off()
	sink()

}

#variance plots
png(filename=paste(outputDir,"/","variancePlot.png",sep=""))
plot(log(variances[1:min(showMaxPC,length(variances))]),xlab="principal components",ylab="log(variance)",type="b",pch=16)
sink("/dev/null")
dev.off()
sink()

png(filename=paste(outputDir,"/","variancePlotNL.png",sep=""))
plot(variances[1:min(showMaxPC,length(variances))],xlab="principal components",ylab="variance",type="b",pch=16)
sink("/dev/null")
dev.off()
sink()

cumulative =function(L)
{
	cL=L
	cL[1]=L[1]
	for(i in 2:length(L)){
		cL[i]=cL[i-1]+L[i]	
	}
	return(cL)
}

sumOfVariances=sum(sd^2)
variancesProportion=variances/sumOfVariances*100
variancesCdf=cumulative(variancesProportion)
variancesCdfOffset=variancesCdf-variancesProportion
png(filename=paste(outputDir,"/","variancePlotProportion.png",sep=""))
barplot(rbind(variancesProportion[1:min(showMaxPC,length(variances))], variancesCdfOffset[1:min(showMaxPC,length(variances))]),xlab="principal components",ylab="variance proportion (%)",pch=16,ylim=c(0,100),names.arg=1:min(showMaxPC,length(variances)),col=c("red","grey"))


sink("/dev/null")
dev.off()
sink()



#write tables
loadingOut=paste(outputDir,"/","loading.txt",sep="")
scoresOut=paste(outputDir,"/","scores.txt",sep="")
sdOut=paste(outputDir,"/","sd.txt",sep="")

options(warn=-1)
cat("X\t",file=loadingOut)
write.table(loadings,file=loadingOut,sep=separator,append=TRUE,quote=FALSE)
cat("X\t", file=scoresOut)
write.table(scores,file=scoresOut,sep=separator,append=TRUE,quote=FALSE)
cat("PC\t", file=sdOut)
write.table(cbind(sd=sd,variance=variances,variancePdf=variancesProportion/100.0,varainceCdf=variancesCdf/100.0),file=sdOut,sep=separator,append=TRUE,quote=FALSE)
