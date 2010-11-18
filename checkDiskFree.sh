#!/bin/bash

orig=`pwd`
cd /lab/solexa_jaenisch
cd /lab/solexa_jaenisch2
cd /lab/solexa_jaenisch3
cd /lab/jaenisch_albert
cd /lab/jaenisch_albert2

cd $orig

df -h | grep jaenisch
