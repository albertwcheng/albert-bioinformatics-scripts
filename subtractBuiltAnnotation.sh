
if [ $# -lt 3 ]; then
	echo $0 subtractee subtractor subtracted
	echo "Gene level subtraction. Assume having header"
	exit
fi

subtractee=$1
subtractor=$2
subtracted=$3

tmp0=$subtracted.tmp0
tmp1=$subtracted.tmp1
tmp2=$subtracted.tmp2
tmp3=$subtracted.tmp3
tmp4=$subtracted.tmp4
tmp5=$subtracted.tmp5
tmp6=$subtracted.tmp6
tmp7=$subtracted.tmp7

rm -f $tmp1
rm -f  $tmp2
rm -f  $tmp3
rm -f $tmp4
rm -f  $tmp5
rm -f  $tmp6
rm -f  $tmp7

splitlines.py $subtractee 1 $tmp0,$tmp6

joinBedByOverlap.py $tmp6 $subtractor > $tmp1

cuta.py -f4 $tmp1 | awk '{split($0,a,"."); name=a[1]; for(i=2;i<=length(a)-1;i++){name=name a[i];} printf("%s\n",name);}' | sort | uniq > $tmp2 #tmp2 is now the gene in subtractee overlapped by subtractor

#append a row in subtractee the gene name
awk '{split($4,a,"."); name=a[1]; for(i=2;i<=length(a)-1;i++){name=name a[i];} printf("%s\t%s\n",$0,name);}' $tmp6 > $tmp3

#now cut out the last column of tmp3 to tmp4
cuta.py -f_1 $tmp3 > $tmp4

subtractSets.py $tmp4 $tmp2 > $tmp5
#tmp5 is now the gene not overlapped by subtractor at gene level

cat $tmp0 > $subtracted
joinu.py -r -1 _1 -2 _1 $tmp5 $tmp3 > $tmp7

cuta.py -f1-_2 $tmp7 >> $subtracted #remove the last column=gene name



rm $tmp1
rm $tmp2
rm $tmp3
rm $tmp4
rm $tmp5
rm $tmp6
rm $tmp7