#!/bin/bash


if [ $# -lt 7 ]; then
	echo $0 Infile GeneIDCol class1label class1cols class2label class2cols outprefix
	echo "make outprefix.exp.txt and outprefix.cls and outprefix.mwtcls"
	exit
fi

Infile=$1
GeneIDCol=$2
class1label=$3
class1cols=$4
class2label=$5
class2cols=$6
outprefix=$7


function repeatNTimes {
	S=$1
	n=$2
	echo `python -c "print ' '.join(['$S']*$n)"`
}

#k=`repeatNTimes "a" 10`
#echo $k
tmp1=`mktemp`
tmp2=`mktemp`
cuta.py -f$GeneIDCol,$class1cols $Infile > $tmp1
#how many columns for tmp1?
colTmp1=`colNum.sh $tmp1`

colTmp1=`expr $colTmp1 - 1`
cuta.py -f$class2cols $Infile > $tmp2
colTmp2=`colNum.sh $tmp2`

numSam=`expr $colTmp1 + $colTmp2`
numCls=2
#create phenotype file
echo "$numSam $numCls 1" > $outprefix.cls
echo "# $class1label $class2label" >> $outprefix.cls
class1flag=`repeatNTimes "0" $colTmp1`
class2flag=`repeatNTimes "1" $colTmp2`
echo "$class1flag $class2flag" >> $outprefix.cls

echo "NA $class1flag $class2flag" | tr " " "," > $outprefix.mwtcls #ignore gene ID

tmp3=`mktemp`
tmp4=`mktemp`
awk -v FS="\t" -v OFS="\t" -v suffix=$class1label '{if(FNR==1){for(i=2;i<=NF;i++){$i=$i "_as_" suffix "_" i-1 }}print;}' $tmp1 > $tmp3
awk -v FS="\t" -v OFS="\t" -v suffix=$class2label '{if(FNR==1){for(i=1;i<=NF;i++){$i=$i "_as_" suffix "_" i }}print;}' $tmp2 > $tmp4
#now make the expression submatrix
paste $tmp3 $tmp4 > $outprefix.exp.txt
#done

rm $tmp1
rm $tmp2
rm $tmp3
rm $tmp4
