#!/usr/bin/env python

'''



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

'''


import math as Math
from sys import *
from getopt import getopt

# test statistically whether there is any relation between two categorical variables (with two levels). 
# Created by: Oyvind Langsrud


#
# Copyright (C) : All right reserved. 
# Contact Oyvind Langsrud for permission.
# 
# Not intended for public release without contacting original author

# Translated by Albert Cheng to Python

def lngamm(z):
# Reference: "Lanczos, C. 'A precision approximation 
# of the gamma function', J. SIAM Numer. Anal., B, 1, 86-96, 1964."
# Translation of  Alan Miller's FORTRAN-implementation
# See http:#lib.stat.cmu.edu/apstat/245

  x = 0.0;
  x += 0.1659470187408462e-06/(z+7);
  x += 0.9934937113930748e-05/(z+6);
  x -= 0.1385710331296526    /(z+5);
  x += 12.50734324009056     /(z+4);
  x -= 176.6150291498386     /(z+3);
  x += 771.3234287757674     /(z+2);
  x -= 1259.139216722289     /(z+1);
  x += 676.5203681218835     /(z);
  x += 0.9999999999995183;
  return(Math.log(x)-5.58106146679532777-z+(z-0.5)*Math.log(z+6.5));




def lnfact(n):
  if(n<=1):
    return(0);
		
  return(lngamm(n+1));


def lnbico(n,k):
  return(lnfact(n)-lnfact(k)-lnfact(n-k));


def hyper_323(n11,n1_,n_1,n):
  return(Math.exp(lnbico(n1_,n11)+lnbico(n-n1_,n_1-n11)-lnbico(n,n_1)));



def hyper(n11,sn11,sn1_,sn_1,sn,sprob):
  return(hyper0(n11,0,0,0,sn11,sn1_,sn_1,sn,sprob));


def hyper0(n11i,n1_i,n_1i,ni,sn11,sn1_,sn_1,sn,sprob):
   
  
  #if(not (n1_i | n_1i | ni)):
  if n1_i==0 and n_1i==0 and ni==0:
    if(not (n11i % 10 == 0)):
      if(n11i==sn11+1):  
	    sprob *= ((sn1_-sn11)/(n11i))*((sn_1-sn11)/(n11i+sn-sn1_-sn_1));
	    sn11 = n11i;
	    return [sn11,sn1_,sn_1,sn,sprob];
      if(n11i==sn11-1):
	    sprob *= ((sn11)/(sn1_-n11i))*((sn11+sn-sn1_-sn_1)/(sn_1-n11i));
	    sn11 = n11i;
	    return [sn11,sn1_,sn_1,sn,sprob];
    sn11 = n11i;
  else:
    sn11 = n11i;
    sn1_=n1_i;
    sn_1=n_1i;
    sn=ni;
  sprob = hyper_323(sn11,sn1_,sn_1,sn);
  return [sn11,sn1_,sn_1,sn,sprob];



def exact(n11,n1_,n_1,n):
  sn11=0
  sn1_=0
  sn_1=0
  sn=0
  sprob=0
  
  p=0
  i=0
  j=0
  prob=0
  max_=n1_;
  if(n_1<max_):
    max_=n_1;
  min_ = n1_+n_1-n;
  if(min_<0):
    min_=0;
  if(min_==max_):
  
    sless = 1;
    sright= 1;
    sleft = 1;
    slarg = 1;
    return 1;
    
  #print >> stderr,"a"
  sn11,sn1_,sn_1,sn,sprob=hyper0(n11,n1_,n_1,n,sn11,sn1_,sn_1,sn,sprob);
  prob=sprob
  
  
  sleft=0;
  sn11,sn1_,sn_1,sn,sprob=hyper(min_,sn11,sn1_,sn_1,sn,sprob);
  p=sprob
  i=float(min_+1);
  
  while(p<0.99999999*prob):
    sleft += p;
    sn11,sn1_,sn_1,sn,sprob=hyper(i,sn11,sn1_,sn_1,sn,sprob);
    p=sprob
    i+=1
    
  i-=1;
  #print >> stderr,"b"
  if(p<1.00000001*prob):
    sleft += p;
  else:
    i-=1;
  
  sright=0;
  sn11,sn1_,sn_1,sn,sprob=hyper(max_,sn11,sn1_,sn_1,sn,sprob);
  p=sprob
  #print >> stderr,"c",sleft  
  j=float(max_-1)
  while( p<0.99999999*prob):
    sright += p;
    sn11,sn1_,sn_1,sn,sprob=hyper(j,sn11,sn1_,sn_1,sn,sprob);
    p=sprob
    #print >> stderr,"doing j=",j,p,max_,0.99999999*prob
    j-=1
   
  #print >> stderr,"d"    
  j+=1;
  
  if(p<1.00000001*prob):
    sright += p;
  else:
    j+=1;
    
  if(abs(i-n11)<abs(j-n11)):
    sless = sleft;
    slarg = 1 - sleft + prob;
  else:
    sless = 1 - sright + prob;
    slarg = sright;
    
  return [sleft,sless,slarg,sright,prob];

   




def exact22(n11_,n12_,n21_,n22_):
  newline="\n"
##  var n11_ = parseInt("0"+n11,10);
#  var n12_ = parseInt("0"+n12,10);
#  var n21_ = parseInt("0"+n21,10);
#  var n22_ = parseInt("0"+n22,10);
  if(n11_<0):
    n11_ *= -1;
  if(n12_<0):
    n12_ *= -1;
  if(n21_<0):
    n21_ *= -1;
  if(n22_<0):
    n22_ *= -1; 

  

  n1_ = n11_+n12_;
  n_1 = n11_+n21_;
  n   = n11_ +n12_ +n21_ +n22_;
  sleft,sless,slarg,sright,prob=exact(n11_,n1_,n_1,n);
  
  left    = sless;
  right   = slarg;
  twotail = sleft+sright;
  if(twotail>1):
    twotail=1;
    
  #print >> stderr,  "TABLE = [",n11_,",", n12_,",",n21_,",",n22_,"]"
  #print >> stderr, "Left   : p-value =", left  
  #print >> stderr, "Right  : p-value =", right 
  #print >> stderr, "2-Tail :p-value =", twotail
  return left,right,twotail




if __name__=="__main__":
  def printUsageAndExit(programName):
    print >> stderr,programName,"[option] n11 n12 n21 n22"
    print >> stderr,'Options:'
    print >> stderr,'--simple-output: output as n11 n12 n21 n22 leftpvalue rightpvalue 2tailpvalue'
    exit()
    
  programName=argv[0]
  opts,args=getopt(argv[1:],'','simple-output')
  
  simple=False
  
  for o,v in opts:
  	if o=='--simple-output':
  	  simple=True
  	  

  try: 
    n11_=int(args[0])
    n12_=int(args[1])
    n21_=int(args[2])
    n22_=int(args[3])
  except:
    printUsageAndExit(programName)
  
  
  left,right,twotail=exact22(n11_,n12_,n21_,n22_)
  if simple:
    print >> stdout,n11_,n12_,n21_,n22_,left,right,twotail
  else:
    print >> stdout,  "TABLE = [",n11_,",", n12_,",",n21_,",",n22_,"]"
    print >> stdout, "Left   : p-value =", left  
    print >> stdout, "Right  : p-value =", right 
    print >> stdout, "2-Tail : p-value =", twotail
