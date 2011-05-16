
if [ $# -lt 1 ]; then
	echo $0 csvfileNames
	exit
fi

while [ $# -gt 0 ]; do
	i=$1
	shift
	echo processing $i

	tabfileName=${i/.csv/}
	tabfileName=${tabfileName//\ /}.tab
	if [ -e $tabfileName ]; then
		rm -f $tabfileName
	fi
	echo -e "ChamberID\tSampleName\tSampleType\tSamplerConc\tFAMMGBName\tFAMMGBType\tCtValue\tCtQuality\tCtCall\tCtThreshold" > "$tabfileName"
	awk 'FNR>=13' "$i" | tr "," "\t" >> "$tabfileName" #this first 13 rows are useless
	
done