#!/usr/bin/python

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
#extract block from meme.txt

if len(argv)<2 :
	filename="meme.html"
else:
	filename=argv[1]
	
mode=0
nblocks=0

fil=open(filename)
for lin in fil:
	lin=lin.rstrip()
	try:
		if lin.index(">") or lin.index("<"):
			continue
	except:
		pass
	
	if lin[0:4]=='BL  ':
		if mode!=0:
			print >> stderr,"previous motif not properly closed. abort"
			exit()
			
		mode=1
		try:
			wIx=lin.index("width")
		except:
			print >> stderr,"error width not fonund with BL for line",lin
			exit()
			
		nameMotif=lin[2:wIx].strip()
		nameMotifOut="_".join(nameMotif.split())+".block"
		print >> stderr, "got motif", nameMotif , "as",nameMotifOut
		motifFout=open(nameMotifOut,"w")
	elif mode==1: 
		if lin[0:2]=="//":
			print >> stderr, "motif",nameMotif,"ended"
			mode=0	
			motifFout.close()
			nblocks+=1
		else:
			print >> motifFout,lin
		

fil.close()
if mode!=0:
	print >> stderr,"last motif not properly closed. abort"
	exit()		
	

print >> stderr,"<extraction successful>:total blocks:",nblocks
