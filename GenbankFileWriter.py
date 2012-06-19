

class GenbankFileWriter:
	def __init__(self,_locusName):
		self.locusName=_locusName
		self.features=[]
		self.sequence=""
		self.definition=None
		self.accession=""
		self.keywords="."
		self.source=""
		self.organism=""
		
	def intStrFill(self,x,fill):
		s=str(x)
		while(len(s)<fill):
			s=" "+s
			
		return s
	
	def addFeature(self,featureStart1,featureEnd1,strand,featureName):
		self.features.append((featureStart1,featureEnd1,strand,featureName))
	
		
	def writeGenbankFile(self,filename):
		fil=open(filename,"w")
		seqlen=len(self.sequence)
		
		if self.definition==None:
			self.definition=self.locusName
		
		print >> fil,"LOCUS       %s     %d bp    DNA             SYN" %(self.locusName,seqlen)
		print >> fil,"DEFINITION  %s" %(self.definition)
		print >> fil,"ACCESSION   %s" %(self.accession)
		print >> fil,"KEYWORDS    %s" %(self.keywords)
		print >> fil,"SOURCE      %s" %(self.source)
		print >> fil,"  ORGANISM  %s" %(self.organism)
		print >> fil,"FEATURES             Location/Qualifiers"
		print >> fil,"     source          1..%d" %(seqlen)
		print >> fil,"                     /organism=\"%s\"" %(self.organism)
		for feature in self.features:
			featureStart1,featureEnd1,strand,featureName=feature
			print >> fil,"     misc_feature    %s%d..%d%s" %(("complement(" if strand=="-" else ""),featureStart1,featureEnd1,(")" if strand=="-" else ""))
			print >> fil,"                     /label=\"%s\"" %(featureName)

		print >> fil,"ORIGIN"
		
		lfill=len(str(seqlen))
		
		for i in range(0,seqlen,60):
			seqOut=self.intStrFill(i+1,lfill)
			
			for j in range(i,i+60,10):
				seqOut+=" "+self.sequence[j:j+10]
			print >> fil,seqOut
						
		print >> fil,"//"
		fil.close()