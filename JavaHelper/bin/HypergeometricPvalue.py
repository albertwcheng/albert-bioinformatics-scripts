
from subprocess import *
from sys import *


def JHypergeometricPvalue(valuesSamtSamPoptPop,errorValue):
	
	Pvalues=[]

	p = Popen("java HypergeometricPvalue", shell=True,
		  stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

	(child_stdin, child_stdout_and_stderr) = (p.stdin, p.stdout)


	for samt,sam,popt,pop in valuesSamtSamPoptPop[0:4]:
		child_stdin.write(" ".join([str(samt),str(sam),str(popt),str(pop)])+"\n");

	child_stdin.close();

	lines=child_stdout_and_stderr.readlines();
	#print >> stdout,"result from java is ",l

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

