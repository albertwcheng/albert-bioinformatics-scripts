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

from albertcommon import *
from sys import *
from getopt import getopt


if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'',['fs=','internalfs='])

	try:
		filename,colsKey=args
	except:
		print >> stderr,"Usage:",programName,"[options] filename colsKey"
		print >> stderr,"stick values per column on having the same cols keys"
		print >> stderr,"options:"
		print >> stderr,"--fs field-separator"
		print >> stderr,"--internalfs internal field-separator to join collapsed fields"
		exit()

	headerRow=1
	fs="\t"
	internalfs="|"


	for o,v in opts:
		if o=='--fs':
			fs=v
		elif o=='--internalfs':
			internalfs=v

	startRow=headerRow+1

	header,prestarts=getHeader(filename,headerRow,startRow,fs)
		
	colsKey=getCol0ListFromCol1ListStringAdv(header,colsKey)

	
	keys=[] # [(key1,key2,...)]
	lines=[] # same order as keys [{col1values},{col2values},...]

	fil=open(filename)

	lino=0

	for lin in fil:
		lino+=1
		if lino%100==1:
			print >> stderr,"reading in line",lino
		
		lin=lin.rstrip()
		fields=lin.split(fs)
		thisKeys=tuple(getSubvector(fields,colsKey))
		try:
			keyI=keys.index(thisKeys)
		except: #key not present
			keys.append(thisKeys)
			linedata=[]
			lines.append(linedata)
			for i in range(0,len(fields)):
				linedata.append(set([fields[i]]))

			continue
	
		linedata=lines[keyI]
		for i in range(0,len(fields)):
			if i not in colsKey:
				try:
					linedata[i].add(fields[i])
				except IndexError: #for lineData
					llinedata=len(linedata)
					needed=i-llinedata
					for j in range(0,needed):
						linedata.append(set())
					#now add in the new thing
					linedata.append(set([fields[i]]))
	
				
			
		

	fil.close()
	
	#now finish reading, output!

	for linedata in lines:
		#convert!
		for i in range(0,len(linedata)):
			linedata[i]=internalfs.join(list(linedata[i]))
		
		print >> stdout,fs.join(linedata)


