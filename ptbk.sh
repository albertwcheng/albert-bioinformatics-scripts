#!/bin/bash

backupstore=/net/coldfact/data/awcheng/backups
tmpdir=/net/coldfact/data/awcheng/tmp



if [ $# -lt 1 ]
then
	echo "Usage:" $0 "directory [-all]"
	exit
fi

dir=$1
timestamp=$dir/._,_ptbk.last

if [ $# -eq 2 ] && [ $2 == "-all" ]; then
	echo "backup everything"
	if [ -e $timestamp ]; then
		rm $timestamp
	fi
fi


findcmd="find $dir -type f"

if [ -e $timestamp ]; then
	findcmd="$findcmd -newer $timestamp"
fi



cd $dir/.. || exit
datestr=`date '+%Y%m%d%H%M'`
outfile=$tmpdir/$dir-$datestr.tgz

findcmd="$findcmd -fprint $tmpdir/tmplist.$dir-$datestr.00"
#echo $findcmd
eval $findcmd


files=`cat "$tmpdir/tmplist.$dir-$datestr.00"`

if [ ${#files} -eq 0 ]; then
	echo "nothing new; exit"
	exit
fi



#Don't send VIM recovery file (.*.swp)
tar czvlf $outfile -T "$tmpdir/tmplist.$dir-$datestr.00"

echo "TimeStamp file for $0. Don't Modify." > $timestamp
echo -e "File backuped\n$files" >> $timestamp
echo "Now copying this file to $backupstore"
ls -l $outfile
mv $outfile $backupstore
#rm "$tmpdir/tmplist.$dir-$datestr.00"
