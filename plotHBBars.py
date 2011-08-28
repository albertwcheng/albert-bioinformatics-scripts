#!/usr/bin/env python

'''

label<tab>mean<tab>(-)sd<tab>(+)sd<tab>r,g,b,a<tab>mean<tab>(-)sd<tab>(+)sd<tab>r,g,b,a<tab>...

'''


from matplotlib.pyplot import *
from optparse import OptionParser
from sys import *

if __name__=='__main__':

	programName=argv[0]
	parser = OptionParser()
	parser.add_option("--yheight", dest="yheight",help="set height of each bar", type=float, default=10.0)
	parser.add_option("--yspacing",dest="yspacing",help="set spacing of each bar", type=float, default=5.0)
	parser.add_option("--ylabel",dest="ylabel",help="set ylabel",default="Y")
	parser.add_option("--xlabel",dest="xlabel",help="set xlabel",default="X")
	parser.add_option("--title",dest="title",help="set title",default="%filename%")
	parser.add_option("--fs",dest="fs",help="set field separator",default="\t")
	parser.add_option("--figsize",dest="figsize",help="set fig size w,h",default="5,5")
	
	(options, args) = parser.parse_args()
	
	try:
		infile,outfile=args
	except:
		print >> stderr,programName,"[options] infile outfile"
		parser.print_help()
		exit()
	
	cury=0
	ylabels=[]
	
	yticks=[]
	
	
	figsiz=options.figsize.split(",")
	figsiz[0]=int(figsiz[0])
	figsiz[1]=int(figsiz[1])
	
	figure(figsize=tuple(figsiz))
	
	if options.title=="%filename%":
		options.title=infile
	
	fil=open(infile)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		fields=lin.split(options.fs)
		ylabels.append(fields[0])
		cury+=options.yspacing
		thisxranges=[]
		facecolors=[]
		thisyrange=(cury,options.yheight)
		
		yticks.append(cury+options.yheight/2)
		
		for i in range(1,len(fields),3): #4
			#mean,sd1,sd2,rgba=fields[i:i+4]
			#mean=float(mean)
			#sd1=float(sd1)
			#sd2=float(sd2)
			x,width,rgba=fields[i:i+3]
			x=float(x)
			width=float(width)
			r,g,b,a=rgba.split(",")
			
			r=float(r)
			g=float(g)
			b=float(b)
			a=float(a)
			#thisxranges.append((mean-sd1,sd1))
			#thisxranges.append((mean,sd2))
			thisxranges.append((x,width))
			facecolors.append((r,g,b,a))
		
		
		broken_barh(thisxranges,thisyrange,facecolors=facecolors)
		cury+=options.yheight	
		
	fil.close()
	
	ylim(0,cury+options.yspacing)
	
	

	#ylim(5,35)
	#xlim(0,200)
	xlabel(options.xlabel)
	ylabel(options.ylabel)
	title(options.title)
	gca().set_yticks(yticks)
	gca().set_yticklabels(ylabels)
	#grid(True)
	
	savefig(outfile)