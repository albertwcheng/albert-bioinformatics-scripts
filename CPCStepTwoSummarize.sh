#!/bin/bash

if [ $# -lt 4 ]; then
	echo $0 "CPCOutputDir SummaryDir isoformIdx[-1] [ [ bedFiles ] ... ]"
	exit
fi

numArgs=$#

CPCOutputDir=$1
SummaryDir=$2
isoformIdx=$3
shift
shift
shift






#exit


CPCOutputDir=`abspath.py $CPCOutputDir`
SummaryDir=`abspath.py $SummaryDir`

echo CPCOutputDir=$CPCOutputDir
echo SummaryDir=$SummaryDir

mkdir.py $SummaryDir

:<<'COMMENT'
chr1:226760-226928_adipose.1.HBM	168	noncoding	-1.24382
chr1:226760-226928_adipose.1.HBM(revcomp)	168	noncoding	-1.49897
chr1:654553-654770_adipose.1.HBM	217	noncoding	-0.451318
chr1:654553-654770_adipose.1.HBM(revcomp)	217	coding	1.23503
chr1:752926-778790_adipose.1.HBM	706	coding	0.484315
chr1:752926-778790_adipose.1.HBM(revcomp)	706	noncoding	-0.262217
chr1:753322-778790_adipose.1.HBM	662	coding	0.507055
chr1:753322-778790_adipose.1.HBM(revcomp)	662	noncoding	-1.05842
chr1:779076-779321_adipose.1.HBM	245	noncoding	-1.25563
chr1:779076-779321_adipose.1.HBM(revcomp)	245	noncoding	-1.40245
COMMENT

cat $CPCOutputDir/*.resultTab > $SummaryDir/merged.cpc.resultTab
cat $CPCOutputDir/evidence/*/*.homo > $SummaryDir/merged.cpc.evidence.homo
cat $CPCOutputDir/evidence/*/*.orf > $SummaryDir/merged.cpc.evidence.orf

#filter only sense
awk -v FS="\t" -v OFS="\t" '$1!~/\(revcomp\)/' $SummaryDir/merged.cpc.resultTab > $SummaryDir/merged.sense.cpc.resultTab
awk -v FS="\t" -v OFS="\t" '$1!~/\(revcomp\)/' $SummaryDir/merged.cpc.evidence.homo > $SummaryDir/merged.sense.cpc.evidence.homo
awk -v FS="\t" -v OFS="\t" '$1!~/\(revcomp\)/' $SummaryDir/merged.cpc.evidence.orf > $SummaryDir/merged.sense.cpc.evidence.orf

#merge into one row for sense and revcomp, and also into one row per gene
awk -v FS="\t" -v OFS="\t" '{gsub(/\(revcomp\)/,"",$1); print;}' $SummaryDir/merged.cpc.resultTab > $SummaryDir/merged.cpc.resultTab.colstrand.00
stickColValues.py $SummaryDir/merged.cpc.resultTab.colstrand.00 1 > $SummaryDir/merged.cpc.resultTab.colstrand
	
if [[ $isoformIdx != 0 ]]; then
	
	awk -v FS="\t" -v OFS="\t" -v isoformIdx=$isoformIdx '{split($1,a,".");geneName=a[1]; for(i=2;i<length(a)+1+isoformIdx;i++){ geneName= geneName "." a[i]} for(i=length(a)+isoformIdx+2;i<=length(a);i++){ geneName=geneName "." a[i] } $1=geneName; print;}' $SummaryDir/merged.cpc.resultTab.colstrand > $SummaryDir/merged.cpc.resultTab.colgene.00
	awk -v FS="\t" -v OFS="\t" -v isoformIdx=$isoformIdx '{split($1,a,".");geneName=a[1]; for(i=2;i<length(a)+1+isoformIdx;i++){ geneName= geneName "." a[i]} for(i=length(a)+isoformIdx+2;i<=length(a);i++){ geneName=geneName "." a[i] } $1=geneName; print;}' $SummaryDir/merged.sense.cpc.resultTab > $SummaryDir/merged.sense.cpc.resultTab.colgene.00
	stickColValues.py --printlino 10000 $SummaryDir/merged.cpc.resultTab.colgene.00  1 > $SummaryDir/merged.cpc.resultTab.colgene
	stickColValues.py --printlino 10000  $SummaryDir/merged.sense.cpc.resultTab.colgene.00 1 >  $SummaryDir/merged.sense.cpc.resultTab.colgene
	
else
	ln -f $SummaryDir/merged.cpc.resultTab.colstrand $SummaryDir/merged.cpc.resultTab.colgene
	ln -f $SummaryDir/merged.sense.cpc.resultTab $SummaryDir/merged.sense.cpc.resultTab.colgene
fi

for i in $SummaryDir/merged.cpc.resultTab.colgene $SummaryDir/merged.sense.cpc.resultTab.colgene $SummaryDir/merged.cpc.resultTab.colstrand; do
	awk -v FS="\t" -v OFS="\t" '{split($3,a,"|"); coding="noncoding"; for(i=1;i<=length(a);i++){if(a[i]=="coding"){coding="coding"; break;}} printf("%s\t%s\n",$1,coding)}' $i > $i.simp
	awk -v FS="\t" -v OFS="\t" '$2=="coding"' $i.simp > $i.coding
	awk -v FS="\t" -v OFS="\t" '$2=="noncoding"' $i.simp > $i.noncoding
done


mkdir $SummaryDir/bisense_gl_coding
mkdir $SummaryDir/bisense_gl_noncoding
mkdir $SummaryDir/sense_gl_coding
mkdir $SummaryDir/sense_gl_noncoding
mkdir $SummaryDir/geneTranscriptMaps

#now for each bed file
for((i=4;i<=$numArgs;i++)); do
	bedFile=$1
	echo processing $bedFile
	bnbedFile=`basename $bedFile`
	bnbedFile=${bnbedFile/.bed/}
	bnbedFile=${bnbedFile/.ebed/}
	if [[ $isoformIdx != 0 ]]; then
		awk -v FS="\t" -v OFS="\t" -v isoformIdx=$isoformIdx '{split($4,a,".");geneName=a[1]; for(i=2;i<length(a)+1+isoformIdx;i++){ geneName= geneName "." a[i]} for(i=length(a)+isoformIdx+2;i<=length(a);i++){ geneName=geneName "." a[i] } printf("%s\t%s\n",geneName,$4);}' $bedFile > $SummaryDir/$bnbedFile.map
	else
		awk -v FS="\t" -v OFS="\t" '{printf("%s\t%s\n",$4,$4);}' $bedFile > $SummaryDir/$bnbedFile.map
	fi
		
	joinu.py $SummaryDir/merged.sense.cpc.resultTab.colgene.coding $SummaryDir/$bnbedFile.map > $SummaryDir/merged.sense.cpc.resultTab.colgene.coding.toTranscriptMap
	#col2 is transcript name
	joinu.py -1 3 -r -2 4 $SummaryDir/merged.sense.cpc.resultTab.colgene.coding.toTranscriptMap $bedFile > $SummaryDir/sense_gl_coding/$bnbedFile.sense_gl_coding.bed
	ln -f $SummaryDir/sense_gl_coding/$bnbedFile.sense_gl_coding.bed $SummaryDir/sense_gl_coding/$bnbedFile.bed 
	
	joinu.py $SummaryDir/merged.sense.cpc.resultTab.colgene.noncoding $SummaryDir/$bnbedFile.map > $SummaryDir/merged.sense.cpc.resultTab.colgene.noncoding.toTranscriptMap
	#col2 is transcript name
	joinu.py -1 3 -r -2 4 $SummaryDir/merged.sense.cpc.resultTab.colgene.noncoding.toTranscriptMap $bedFile > $SummaryDir/sense_gl_noncoding/$bnbedFile.sense_gl_noncoding.bed
	ln -f  $SummaryDir/sense_gl_noncoding/$bnbedFile.sense_gl_noncoding.bed $SummaryDir/sense_gl_noncoding/$bnbedFile.bed
	
	
	joinu.py $SummaryDir/merged.cpc.resultTab.colgene.coding $SummaryDir/$bnbedFile.map > $SummaryDir/merged.cpc.resultTab.colgene.coding.toTranscriptMap
	#col2 is transcript name
	joinu.py -1 3 -r -2 4 $SummaryDir/merged.cpc.resultTab.colgene.coding.toTranscriptMap $bedFile > $SummaryDir/bisense_gl_coding/$bnbedFile.bisense_gl_coding.bed
	ln -f $SummaryDir/bisense_gl_coding/$bnbedFile.bisense_gl_coding.bed $SummaryDir/bisense_gl_coding/$bnbedFile.bed 
	
	joinu.py $SummaryDir/merged.cpc.resultTab.colgene.noncoding $SummaryDir/$bnbedFile.map > $SummaryDir/merged.cpc.resultTab.colgene.noncoding.toTranscriptMap
	#col2 is transcript name
	joinu.py -1 3 -r -2 4 $SummaryDir/merged.cpc.resultTab.colgene.noncoding.toTranscriptMap $bedFile > $SummaryDir/bisense_gl_noncoding/$bnbedFile.bisense_gl_noncoding.bed
	ln -f  $SummaryDir/bisense_gl_noncoding/$bnbedFile.bisense_gl_noncoding.bed $SummaryDir/bisense_gl_noncoding/$bnbedFile.bed
	
done
