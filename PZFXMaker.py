#!/usr/bin/env python
from sys import *

def writePzfxTable(stream,tableRefID,tableTitle,YColWidth,Decimals,DataT):
	#DataT=[ [colName, colValues=[ ] ] ]
	print >> stream,'<Table ID="'+tableRefID+'" XFormat="none" TableType="OneWay">'
	print >> stream,'<Title>'+tableTitle+'</Title>'
	
	for colName,colValues in DataT:
		print >> stream,'<YColumn Width="'+str(YColWidth)+'" Decimals="'+str(Decimals)+'" Subcolumns="1">'
		print >> stream,'<Title>'+colName+'</Title>'
		print >> stream,'<Subcolumn>'
		for colValue in colValues:
			print >> stream,"<d>"+str(colValue)+"</d>"
		print >> stream,'</Subcolumn>'
		print >> stream,'</YColumn>'
	
	print >> stream,'</Table>'
	
def writePzfxTableFile(outFile,pzfxTemplateFile,tableRefID,tableTitle,YColWidth,Decimals,DataT):
	pzfxTemplateFile=open(pzfxTemplateFile)
	outStream=open(outFile,"w")
	tableArea=False
	for lin in pzfxTemplateFile:
		lin=lin.rstrip("\r\n")
		if len(lin)>0:
			if lin[:7]=="<Table ":
				tableArea=True
				writePzfxTable(outStream,tableRefID,tableTitle,YColWidth,Decimals,DataT)
			elif lin=="</Table>":
				tableArea=False
			elif not tableArea:
				print >> outStream,lin
		else:
			print >> outStream,lin
		
	pzfxTemplateFile.close()
	outStream.close()
	
if __name__=='__main__':
	print >> stderr,"try"
	DataT=[]
	DataT.append( ["columnA", [12,35,23.5,32.3] ] )
	DataT.append( ["columnB", [457,23] ] )
	writePzfxTableFile("try.pzfx","template.pzfx","Table0","Gene Plot","80",3,DataT)