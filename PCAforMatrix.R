#!/usr/bin/env Rscript

args <- commandArgs(TRUE)


largs <- length(args)

if(largs<2){
	print("Usage: Rscript PCAforMatrix.R matrixFileName outputDir center=yes scale=yes sep=tab drawcomponents=1,2 ...")
	quit()	
}


center="yes"
scale="yes"
separator="\t"
matrixFileName=args[1]
outputDir=args[2]

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
				for(i in 6:largs){
					fields=as.numeric(unlist(strsplit(args[i],",")))
					drawcomponents=cbind(drawcomponents,fields)				}
				
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
plot(log(variances),xlab="principal components",ylab="log(variance)",type="b",pch=16)
sink("/dev/null")
dev.off()
sink()

png(filename=paste(outputDir,"/","variancePlotNL.png",sep=""))
plot(variances,xlab="principal components",ylab="variance",type="b",pch=16)
sink("/dev/null")
dev.off()
sink()

sumOfVariances=sum(sd^2)
png(filename=paste(outputDir,"/","variancePlotProportion.png",sep=""))
barplot(variances/sumOfVariances*100,xlab="principal components",ylab="variance proportion (%)",pch=16,ylim=c(0,100),names.arg=1:length(variances))
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
write.table(sd,file=sdOut,sep=separator,append=TRUE,quote=FALSE)
