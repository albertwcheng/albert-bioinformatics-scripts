


def printOcarinon_sub_circle(stream,cx,cy,r,sw,on,scale):
	print >> stream,"<circle cx=\""+str(cx*scale)+"\" cy=\""+str(cy*scale)+"\" r=\""+str(r*scale)+"\" stroke=\"black\" stroke-width=\""+str(sw*scale)+"\" "
	if on:
		print >> stream,"fill=\"black\"/>"
	else:
		print >> stream,"fill=\"white\"/>"

def printOcarinon_sub(stream,ABCDCode,scale,curx,cury):

	A,B,C,D=ABCDCode
	
	if A:
		printOcarinon_sub_circle(stream,curx+0.0,cury+0.0,20,2.0,1,scale)
	
	if B:
		printOcarinon_sub_circle(stream,curx+0.0,cury+50.0,20,2.0,1,scale)
	if C:
		printOcarinon_sub_circle(stream,curx+50.0,cury+0.0,20,2.0,1,scale)	
		
	if D:
		printOcarinon_sub_circle(stream,curx+50.0,cury+50.0,20,2.0,1,scale)			
		
	curx+=110
	return curx,cury


letterToOcarinaABCD={ "C'": (0,0,0,0), "G#,": (1,0,0,0), "A": (0,0,1,0), "Bb":(0,0,0,1), "B":(0,1,0,0), "Bb,":(1,1,0,0), "F":(1,0,1,0), "A,":(1,0,0,1), "G#":(0,1,1,0), "G,":(0,1,0,1), "G":(0,0,1,1), "B,":(1,1,0,1), "E":(1,1,1,0), "D":(1,0,1,1), "C": (1,1,1,1)}

def printOcarinon(stream,letter,scale,curx,cury): #return new curx, cury
	global letterToOcarinaABCD
	return printOcarinon_sub(letterToOcarinaABCD,letterToOcarinaABCD[letter],scale,curx,cury)
	
	

def createSVGFromLetterScore(stream,letterScore,scale):
	print >> stream, "<?xml version=\"1.0\" standalone=\"no\"?>"
	print >> stream, "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\""
	print >> stream, "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
	print >> stream, "<svg width=\"100%\" height=\"100%\" version=\"1.1\""
	print >> stream, "xmlns=\"http://www.w3.org/2000/svg\">"
	
	curx=30
	cury=30
	
	for letter in letterScore.split(" "):
		curx,cury=printOcarinon(stream,letter,scale,curx,cury)
	
	
	
	
	print >> stream, "</svg>"

def printUsageAndExit(programName):
	print >> stderr,programName,"letterScore scale"
	exit(1)
	
if __name__='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		letterScore,scale=args
	except:
		printUsageAndExit(programName)
		
	scale=float(scale)
	createSVGFromLetterScore(stdout,letterScore,scale)