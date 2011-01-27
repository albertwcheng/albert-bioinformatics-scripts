#!/bin/bash

if [ $# -ne 5 ];then
	echo $0 "file1 col1 file2 col2 skipNLines"
	echo "Can use column directives"
	exit
fi

file1=$1
col1=$2
file2=$3
col2=$4
skipNLines=$5

tmp1=`mktemp`
tmp2=`mktemp`
tmp3=`mktemp`
tmp4=`mktemp`
if [[ $skipNLines != 0 ]]; then
cuta.py -f"$col1" $file1 | awk "FNR>$skipNLines" | sort | uniq > $tmp1
cuta.py -f"$col2" $file2 | awk "FNR>$skipNLines" | sort | uniq >  $tmp2
else
cuta.py -f"$col1" $file1 | sort | uniq > $tmp1
cuta.py -f"$col2" $file2 | sort | uniq > $tmp2
fi

uniq1=`wc -l $tmp1 | cut -d" " -f1`
uniq2=`wc -l $tmp2 | cut -d" " -f1`
subtractSets.py $tmp1 $tmp2 > $tmp4 2> /dev/null
tmp1only=`wc -l $tmp4 | cut -d" " -f1`
intersection=`expr $uniq1 - $tmp1only`
tmp2only=`expr $uniq2 - $intersection`
union=`expr $uniq1 + $tmp2only`

file1bn=`basename $file1`
file2bn=`basename $file2`

echo "Items1=$uniq1 #$file1"
echo "Items2=$uniq2  #$file2"
echo "Intersection=$intersection #$file1bn ^ $file2bn"
echo "ItemsOnly1=$tmp1only #$file1bn - $file2bn"
echo "ItemsOnly2=$tmp2only #$file2bn - $file1bn"
echo "Union=$union #$file1bn V $file2bn"


rm $tmp1
rm $tmp2
rm $tmp3
rm $tmp4