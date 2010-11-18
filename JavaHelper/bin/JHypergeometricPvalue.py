#!/usr/bin/python
from subprocess import *
from sys import *


def JHypergeometricPvalue(valuesSamtSamPoptPop,errorValue):
	
	Pvalues=[]

	p = Popen("java HypergeometricPvalue", shell=True,
		  stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

	(child_stdin, child_stdout_and_stderr) = (p.stdin, p.stdout)


	for entry  in valuesSamtSamPoptPop:
		samt,sam,popt,pop=entry[0:4]
		child_stdin.write(" ".join([str(samt),str(sam),str(popt),str(pop)])+"\n");

	child_stdin.close();

	lines=child_stdout_and_stderr.readlines();
	#print >> stdout,"result from java is ",lines

	child_stdout_and_stderr.close();
	
	if len(lines)!=len(valuesSamtSamPoptPop):
		return Pvalues

	for line in lines:
		line=line.strip()
		try:
			Pvalues.append(float(line))
		except:
			Pvalues.append(errorValue)

	return Pvalues

if __name__=='__main__':
	programName=argv[0]
	try:	
		pop,popt,sam,samt=argv[1:]
		pop=int(pop)
		popt=int(popt)
		sam=int(sam)
		samt=int(samt)

	except:
		print >> stderr,programName,"PopTotal PopSucess SampleTotal SampleSuccess"
		exit()

	Pvalues=JHypergeometricPvalue([[samt,sam,popt,pop]],-1)
	if len(Pvalues)!=1:
		print >> stderr,"Java Hypergeometric Error",Pvalues
		exit()

	print >> stdout,Pvalues[0]
