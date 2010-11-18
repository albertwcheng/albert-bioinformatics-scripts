#!/usr/bin/env python

'''



Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

#BELOW IS COPIED FROM AGAPYTHON Util/Dibase.py ###
###############
###

import string
from sys import *

# change this if the probe labeling changes!
DECODE_DICT = {
    'A0':'A',\
    'A1':'C',\
    'A2':'G',\
    'A3':'T',\
    'A4':'N',\
    'A.':'N',\
    'C0':'C',\
    'C1':'A',\
    'C2':'T',\
    'C3':'G',\
    'C4':'N',\
    'C.':'N',\
    'G0':'G',\
    'G1':'T',\
    'G2':'A',\
    'G3':'C',\
    'G4':'N',\
    'G.':'N',\
    'T0':'T',\
    'T1':'G',\
    'T2':'C',\
    'T3':'A',\
    'T4':'N',\
    'T.':'N',\
    'N0':'N',\
    'N1':'N',\
    'N2':'N',\
    'N3':'N',\
    'N.':'N'\
}

def decodeSequence( encodedSequence ):
    " Converts from 2-base encoding to sequence space "
    currentBase = encodedSequence[0]
    sequence = []
    for i in range(1,len(encodedSequence)):
        dibase = currentBase + encodedSequence[i]
        currentBase = DECODE_DICT[ dibase ]
        sequence.append( currentBase )
    return "".join(sequence)

    


#####
####
#END OF COPY


def printSeqFromCSSeq(csseq):
	if len(csseq)<1:
		return -1
	
	decodedSeq=decodeSequence(csseq)
	print >> stdout,decodedSeq
	return len(decodedSeq)

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	appendingQ='A'
	
	try:
		csfas,=args
	except:
		print >> stderr,"Usage:",programName,"<csfasta|csfastq> > <outfasta|outfastq>"
		exit()
		
	#now
	
	csseq=""
	#lastLineIsPlus=False
	lenseq=-1
	fil=open(csfas)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)<1 or lin[0]=="#":
			continue
		if lin[0] in ["@" , ">", "+", "!"]: #these are nonsequence
			nlenseq=printSeqFromCSSeq(csseq) #flush the sequences first
			if nlenseq!=-1:
				lenseq=nlenseq
			csseq=""
			
			if lin[0]=="!": #this line is the quality score of csfastq files
				if lenseq==len(lin)-1:
					lin=lin[1:] #trim the "!"
			  	elif lenseq==len(lin):
			  		lin=lin[1:]+appendingQ
			  		#print >> stderr,lenseq,len(lin)
			print >> stdout,lin
		else:
			csseq+=lin #continued
	
	fil.close()
	printSeqFromCSSeq(csseq)
	csseq=""
		
	
	
