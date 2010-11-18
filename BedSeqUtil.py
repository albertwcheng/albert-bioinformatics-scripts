#!/usr/bin/python
'''

  For piping between bedSeq program from Python scripts

'''

def toStrArray(L):
	L2=[]
	for x in L:
		L2.append(str(x))
	
	return L2


from subprocess import *

from sys import *

defaultBedSeqCommand=["bedSeq","","/dev/stdin","bed"]

class BedSeqClient:
	child_stdin=None
	child_stderr=None
	child_stdout=None
	def __init__(self,seqDir,bedType,extraParams=None,bedSeqProgramName='bedSeq',inputFileName='/dev/stdin'):
		param=[bedSeqProgramName,seqDir,inputFileName,bedType,"--print-OK"]
		if extraParams:
			param.extend(extraParams)
					
		p=Popen(" ".join(param), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
		(self.child_stdin,self.child_stdout,self.child_stderr)=(p.stdin,p.stdout,p.stderr)
	
	def getBedSeq(self,bedentry):
		if type(bedentry).__name__=="list":
			bedentry="\t".join(toStrArray(bedentry))
		
		print >> self.child_stdin,bedentry
		
		error=self.child_stderr.readline().strip()
		
		if error=="OK":
			result=self.child_stdout.readline().strip()
			return result
		else:
			raise ValueError
			
	def getSeq(self,bedentry):
		result=self.getBedSeq(bedentry)
		fields=result.split("\t")
		return fields[-1]
			
	def close(self):
		self.child_stdin.close()
		self.child_stdout.close()
		self.child_stderr.close()
			


if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		seqDir,=args
	except:
		print >> stderr,programName,"seqDir","> ofile"
		exit()
	
	tries=["chr10\t100225000\t100225200","chr","chr12\t11125235\t11125256"]
	bedSeqClient=BedSeqClient(seqDir,"bed")
	for tri in tries:
		try:
			print >> stdout,bedSeqClient.getBedSeq(tri)
		except:
			pass
	bedSeqClient.close()
	