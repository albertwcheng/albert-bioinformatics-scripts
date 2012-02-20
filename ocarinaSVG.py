#!/usr/bin/env python

from sys import *

def printOcarinon_sub_circle(stream,cx,cy,r,sw,on,scale):
	print >> stream,"<circle cx=\""+str(cx*scale)+"\" cy=\""+str(cy*scale)+"\" r=\""+str(r*scale)+"\" stroke=\"black\" stroke-width=\""+str(sw*scale)+"\" "
	if on:
		print >> stream,"fill=\"black\"/>"
	else:
		print >> stream,"fill=\"white\"/>"

def printOcarinon_sub(stream,ABCDCode,scale,curx,cury):

	A,B,C,D=ABCDCode
	

	printOcarinon_sub_circle(stream,curx+0.0,cury+0.0,20,2.0,A,scale)
	printOcarinon_sub_circle(stream,curx+50.0,cury+0.0,20,2.0,B,scale)
	printOcarinon_sub_circle(stream,curx+0.0,cury+50.0,20,2.0,C,scale)	
	printOcarinon_sub_circle(stream,curx+50.0,cury+50.0,20,2.0,D,scale)			
		
	curx+=110
	return curx,cury

def printUnknown_sub(stream,scale,curx,cury):
	print >> stream, "<rect width=\""+str(90*scale)+"\" height=\""+str(90*scale)+"\" x=\""+str((curx-20)*scale)+"\" y=\""+str((cury-20)*scale)+"\" style=\"fill:grey;\" />"
	curx+=110
	return curx,cury

#letterToOcarinaABCD={ "G,":(0,1,0,1),  "G#,": (1,0,0,0), "A,":(1,0,0,1),  "Bb,":(1,1,0,0),  "B,":(1,1,0,1), "C": (1,1,1,1),  "D":(1,0,1,1), "E":(1,1,1,0), "F":(1,0,1,0),"F#":(0,1,1,1),"G":(0,0,1,1), "G#":(0,1,1,0), "A": (0,0,1,0), "Bb":(0,0,0,1), "B":(0,1,0,0),   "C'": (0,0,0,0)      }

OcarinaABCDToLetter=dict()

_G_=["G,"]
_Gs_=["G#,","Ab,"]
_A_=["A,"]
_As_=["Bb,","A#,"]
_B_=["B,","Cb"]
_C=["C","B#,"]
_D=["D"]
_Ds=["D#","Eb"]
_E=["E","Fb"]
_F=["F","E#"]
_Fs=["F#","Gb"]
_G=["G"]
_Gs=["G#","Ab"]
_A=["A"]
_As=["A#","Bb"]
_B=["B","Cb'"]
__C=["C'","B#"]

Mode="Ionian"
OcarinaABCDToLetter[Mode]=dict()
OcarinaABCDToLetter[Mode][(0,1,0,1)]=_G_
OcarinaABCDToLetter[Mode][(1,0,0,0)]=_Gs_
OcarinaABCDToLetter[Mode][(1,0,0,1)]=_A_
OcarinaABCDToLetter[Mode][(1,1,0,0)]=_As_
OcarinaABCDToLetter[Mode][(1,1,0,1)]=_B_
OcarinaABCDToLetter[Mode][(1,1,1,1)]=_C
OcarinaABCDToLetter[Mode][(1,0,1,1)]=_D
OcarinaABCDToLetter[Mode][(1,1,1,0)]=_E
OcarinaABCDToLetter[Mode][(1,0,1,0)]=_F
OcarinaABCDToLetter[Mode][(0,1,1,1)]=_Fs
OcarinaABCDToLetter[Mode][(0,0,1,1)]=_G
OcarinaABCDToLetter[Mode][(0,1,1,0)]=_Gs
OcarinaABCDToLetter[Mode][(0,0,1,0)]=_A
OcarinaABCDToLetter[Mode][(0,0,0,1)]=_As
OcarinaABCDToLetter[Mode][(0,1,0,0)]=_B
OcarinaABCDToLetter[Mode][(0,0,0,0)]=__C

Mode="Dorian"
OcarinaABCDToLetter[Mode]=dict()
OcarinaABCDToLetter[Mode][(0,1,0,1)]=_G_
OcarinaABCDToLetter[Mode][(1,0,0,0)]=_Gs_
OcarinaABCDToLetter[Mode][(1,0,0,1)]=_A_
OcarinaABCDToLetter[Mode][(1,1,0,0)]=_As_
OcarinaABCDToLetter[Mode][(1,1,0,1)]=_B_
OcarinaABCDToLetter[Mode][(1,1,1,1)]=_C
OcarinaABCDToLetter[Mode][(1,0,1,1)]=_D
OcarinaABCDToLetter[Mode][(1,1,1,0)]=_Ds
OcarinaABCDToLetter[Mode][(1,0,1,0)]=_F
OcarinaABCDToLetter[Mode][(0,1,1,1)]=_Fs
OcarinaABCDToLetter[Mode][(0,0,1,1)]=_G
OcarinaABCDToLetter[Mode][(0,1,1,0)]=_Gs
OcarinaABCDToLetter[Mode][(0,0,1,0)]=_A
OcarinaABCDToLetter[Mode][(0,0,0,1)]=_As
OcarinaABCDToLetter[Mode][(0,1,0,0)]=_As
OcarinaABCDToLetter[Mode][(0,0,0,0)]=__C


#init
letterToOcarinaABCD=dict()

for mode,modeMap in OcarinaABCDToLetter.items():
	
	thisLetterMap=dict()
	
	letterToOcarinaABCD[mode]=thisLetterMap
	
	#swap the key and values.
	for ABCD,letters in modeMap.items():
		for letter in letters:
			thisLetterMap[letter]=ABCD
	
	
	#print >> stderr,mode,thisLetterMap

def printOcarinon(stream,tuning,letter,scale,curx,cury,startx,lino,letterOfLine): #return new curx, cury
	global letterToOcarinaABCD
	
	if letter==".":
		curx=startx
		cury+=110
		return (curx,cury,lino+1,1)
	elif letter=="-":
		curx+=50
		return (curx,cury,lino,letterOfLine+1)	

	try:
		return printOcarinon_sub(stream,letterToOcarinaABCD[tuning][letter],scale,curx,cury)+(lino,letterOfLine+1)
	except:
		print >> stderr,"unknown letter code",letter,"at line",lino,"letter",letterOfLine
		return printUnknown_sub(stream,scale,curx,cury)+(lino,letterOfLine+1)
		

def SVGText(stream,x,y,text,fontFamily,fontSize):
	print >> stream,"<text x=\""+str(x)+"\" y=\""+str(y)+"\" font-family=\""+fontFamily+"\" font-size=\""+str(fontSize)+"\">"+text+"</text>"

def createSVGFromLetterScore(stream,title,tuning,letterScore,scale):

	#scale=0.5
	
	print >> stream, "<?xml version=\"1.0\" standalone=\"no\"?>"
	print >> stream, "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\""
	print >> stream, "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
	print >> stream, "<svg width=\"100%\" height=\"100%\" version=\"1.1\""
	print >> stream, "xmlns=\"http://www.w3.org/2000/svg\">"
	
	#print >> stream, "<g transform=\"scale("+str(_scale)+")\">"
	
	SVGText(stream,10*scale,60*scale,title,"Arial",60*scale)
	SVGText(stream,10*scale,120*scale,tuning,"Arial",30*scale)
	
	startx=30
	starty=30+220
	curx=startx
	cury=starty
	lino=1
	letterOfLine=1
	
	for letter in letterScore.split(" "):
		if len(letter)<1:
			continue
		curx,cury,lino,letterOfLine=printOcarinon(stream,tuning,letter,scale,curx,cury,startx,lino,letterOfLine)
	
	
	
	#print >> stream,"</g>"
	print >> stream, "</svg>"

def printUsageAndExit(programName):
	print >> stderr,programName,"+letterScore/file tuning title subtitle scale outSVG"
	print >> stderr,"create Ocarina Tab score"
	print >> stderr,"input a string of letter score separated by space. allowed letters listed below. Use '.' to indicate new line or '-' to indicate space"
	print >> stderr,"directly specify letter Score by preceding with '+', or use filename"
	#print >> stderr,"allowed letter (ionian tuning):"
	#print >> stderr,"G, G#, A, Bb, B, C D E F F# G G# A Bb B C'"
	exit(1)
	
if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		letterScore,tuning,title,subtitle,scale,outSVG=args
	except:
		printUsageAndExit(programName)
		
	
	
	if letterScore[0]=="+":
		letterScore=letterScore[1:]
	else:
		#load from file
		fil=open(letterScore)
		letterScore=""
		for lin in fil:
			lin=lin.rstrip()
			if len(lin)<1:
				continue
			if lin[0]=='#':
				continue
			letterScore+=lin+" . "
		
	scale=float(scale)
	
	fSVG=open(outSVG,"w")
	createSVGFromLetterScore(fSVG,title,tuning,letterScore,scale)
	fSVG.close()