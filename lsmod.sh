
#!/bin/bash   #to avoid recursive call, this is on second line



basedir=`dirname $0`
#echo $basedir
#echo $0

chmod 777 $basedir/*.sh $basedir/*.py

for i in $basedir/*
do
  if [[ "$i" != *~* ]] && [ ! -d $i ] && [[ `head -n 1 $i` == \#!* ]]; then
  echo `basename $i`
     if [ "$1" == '+' ]; then
       $i
       echo "-------------"
    fi
  fi
done
