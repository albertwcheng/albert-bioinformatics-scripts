#!/usr/bin/python

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