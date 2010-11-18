#!/bin/bash

:<<'COMMENT'



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

COMMENT
#get unique name from a table

if [ $# -lt 2 ]; then
	echo $0 filename colselector [startRow=1]
	exit
fi

filename=$1
colselector=$2

if [ $# -gt 2 ]; then
	startRow=$3
	cuta.py -f"$2" $filename | awk "FNR>=$startRow" |  uniqa.py - >> /dev/stdout 2>> /dev/stderr
else	
	cuta.py -f"$2" $filename | uniqa.py - >> /dev/stdout 2>> /dev/stderr

fi




