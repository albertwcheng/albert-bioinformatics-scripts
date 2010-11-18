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

from sys import *

'''
>mmu-let-7g MIMAT0000121 Mus musculus let-7g
UGAGGUAGUAGUUUGUACAGUU
>mmu-let-7g* MIMAT0004519 Mus musculus let-7g*
ACUGUACAGGCCACUGCCUUGC
>mmu-let-7i MIMAT0000122 Mus musculus let-7i
UGAGGUAGUAGUUUGUGCUGUU
>mmu-let-7i* MIMAT0004520 Mus musculus let-7i*
CUGCGCAAGCUACUGCCUUGCU
'''
def complement(S):
	com=""
	for s in S:	
		if s in ["A", "a"]:
			com+="T"
		elif s in ["T","t","U","u"]:
			com+="A"
		elif s in ["G","g"]:
			com+="C"
		elif s in ["C","c"]:
			com+="G"
		else:
			com+=s

	return com

def reverseString(S):
	rev=""	
	for i in range(len(S)-1,-1,-1):
		rev+=S[i]
	
	return rev

def reverse_complement(S):
	return reverseString(complement(S))
	
 


def out(seqheader,seq):
	if len(seqheader)==0:
		return

	seqheader=seqheader.split(" ")
	name=seqheader[0]
	if name[-1]=='*':
		#star ignored
		return
	miBaseID=seqheader[1]
	miDesc=" ".join(seqheader[2:])
	speciesspecname=name
	name=name.split("-")
	species=name[0]
	
	nonspeciesname="-".join(name[1:])
	rhead8=reverse_complement(seq[0:8])	
	_6mer=rhead8[1:7]
	_7merA1=_6mer+'A'
	_7merM8=rhead8[0:7]
	_8merA1=rhead8[0:7]+'A'

	print >> stdout,"\t".join([species,speciesspecname,nonspeciesname,miBaseID,miDesc,seq,_6mer,_7merA1,_7merM8,_8merA1])


if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		print >> stderr,"filename > outfile"
		exit()

	print >> stdout,"\t".join(["species","speciesspecname","nonspeciesname","miBaseID","Desc","miSeq","6mer","7merA1","7merM8","8merA1"])
	fil=open(filename)

	seqheader=""
	seq=""
	for lin in fil:
		lin=lin.strip()
		if len(lin)<1:
			continue
	
		if lin[0]=='>': #it's a header
			
			out(seqheader,seq)
			seq=""
			seqheader=lin[1:]
		else:
			seq+=lin
		

	fil.close()

	out(seqheader,seq)

