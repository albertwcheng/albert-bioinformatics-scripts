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
from albertcommon import *
import os

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]

	headerRow=1
	fs="\t"
	mulIDsep="/"
	
	try:
		filename,idCol=args
	except:
		print >> stderr,"Usage",programName,"filename idcol"
		exit()
	
	
	idSet=[] #idSet=[ [,...] ]
	idSetLines=[] #idSetLines=[ [ [field,....], ... ] ]

	startRow=headerRow+1

	header,prestarts=getHeader(filename,headerRow,startRow,fs)
		
	idCol=getCol0ListFromCol1ListStringAdv(header,idCol)[0]

	noname_num=0
	
	fil=open(filename)
	
	lino=0
	for lin in fil:
		lino+=1
		if lino<startRow:
			continue

		if lino%100==1:
			#os.system("clear")
			print >> stderr,"processing line",lino
		
		
		lin=lin.rstrip()
		
		if len(lin)==0:
			continue
		
		fields=lin.split(fs)
		
		try:
			idVal=fields[idCol].strip()
		except:
			print >> stderr,"error",fields
			continue
		
		if idVal=="---":
			noname_num+=1
			idVals=["noname_"+str(noname_num)]
		else:
			idVals=idVal.split(mulIDsep)
			
			#remove empties:
			for i in range(len(idVals)-1,-1,-1):
				idValon=idVals[i].strip()
				if len(idValon)==0:
					#empty: remove
					del idVals[i]
				else:
					idVals[i]=idValon #stripped
			
		idGroupToJoin=set()
			
		for idValonI in range(0,len(idVals)):
			idValon=idVals[idValonI] #.strip()				
			#idVals[idValonI]=idValon

			for idGroupI in range(0,len(idSet)):
				if idValon in idSet[idGroupI]:
					idGroupToJoin.add(idGroupI)
				
			#now merge or join
		if len(idGroupToJoin)==0:
			#make a new group
			idSet.append(set(idVals))
			idSetLines.append([fields])
					
		elif len(idGroupToJoin)==1:
			idGroupI=list(idGroupToJoin)[0]
			for idValon in idVals:					
				idSet[idGroupI].add(idValon)
					
			idSetLines[idGroupI].append(fields)
		else: #len > 1
			#mergegroup!
			#using the first idGroupI
			idGroupToJoin=list(idGroupToJoin)
			firstIDGroupI=idGroupToJoin[0]
			firstIDGroup=idSet[firstIDGroupI]
			firstIDLines=idSetLines[firstIDGroupI]					
			for i in range(len(idGroupToJoin)-1,0,-1):
				#move to firstIDGroup
				thisIDGroup=idSet[idGroupToJoin[i]]
				for movee in thisIDGroup:
					firstIDGroup.add(movee)

				firstIDLines.extend(idSetLines[idGroupToJoin[i]])

					#now remove this
				del idSet[idGroupToJoin[i]]
				del idSetLines[idGroupToJoin[i]]
					
					#now add the new stuff in
			for idValon in idVals:
				firstIDGroup.add(idValon)
			
			firstIDLines.append(fields)
					

	fil.close()


	#now output:
	#print header first
	print >> stdout,fs.join(header)
	
	#now go to each united ids and the corresponding line fields
	for uniteID,uniteLines in zip(idSet,idSetLines):
		newID=",".join(list(uniteID))
		for fields in uniteLines:
			#replace ID
			fields[idCol]=newID
			print >> stdout,fs.join(fields)

	
		
