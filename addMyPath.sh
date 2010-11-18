#!/bin/bash

#use source to use me
myPath=`absdirname.py $0`

#echo $myPath

export PATH=${PATH}:${myPath}
