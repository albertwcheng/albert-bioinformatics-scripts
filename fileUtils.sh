#!/bin/sh

function askMkDir {

if [ $# -lt 2 ]; then
	echo "invalid parameters for askMkDir dir default[=y/n]"
	exit
fi

dir=$1
default=$2
echo -ne "Do you want to make dir $dir [y/n] $default?"
while read LINE
do
	
	if [ ${#LINE} -lt 1 ]
	then
		LINE=$default	
	fi
	
	if  [ $LINE == 'y' ] || [ $LINE == 'Y' ]
	then
		mkdir $dir
		return 1
	elif [ $LINE == 'n' ] || [ $LINE == 'N' ]
	then
		return 0
	fi
	
	echo -ne "Do you want to make dir $dir [y/n] $default?"
	
done

}

function askRmDir {

if [ $# -lt 2 ]; then
	echo "invalid parameters for askRmDir dir default[=y/n]"
	exit
fi

dir=$1
default=$2
echo -ne "Do you want to remove dir $dir [y/n] $default?"



while read LINE
do
	#echo ${#LINE}
	
	if [ ${#LINE} -lt 1 ]
	then
		LINE=$default	
	fi
	
	if  [ $LINE == 'y' ] || [ $LINE == 'Y' ]
	then
		rm -R $dir
		return 1
	elif [ $LINE == 'n' ] || [ $LINE == 'N' ]
	then
		return 0
	fi
	
	echo -ne "Do you want to remove dir $dir [y/n] $default?"

	
done

}


function askRmContent {
	
if [ $# -lt 2 ]; then
	echo "invalid parameters for askRmContent dir default[=y/n]"
	exit
fi

#echo "in here"
dir=$1
default=$2
echo -ne "Do you want to remove content of $dir [y/n] $default?"

while read LINE
do
	
	if [ ${#LINE} -lt 1 ]
	then
		LINE=$default	
	fi
	
	if  [ $LINE == 'y' ] || [ $LINE == 'Y' ]
	then
		rm -R $dir/*
		return 1
	elif [ $LINE == 'n' ] || [ $LINE == 'N' ]
	then
		return 0
	fi
	
	echo -ne "Do you want to remove content of $dir [y/n] $default?"
	
done

}

function askMkDirIfNotExist {

if [ $# -lt 2 ]; then
	echo "invalid parameters for askMkDirIfNotExist dir default[=y/n]"
	exit
fi


	dir=$1
	default=$2
	if [ ! -d $dir ]
	then
		echo -ne $dir "does not exist."
		askMkDir $dir $default
		return $?
	fi
	
	return 1
}

function askRmDirContentIfExist {

if [ $# -lt 2 ]; then
	echo "invalid parameters for askRmDirContentIfExist dir default[=y/n]"
	exit
fi

	dir=$1
	default=$2
	
	if [ ! -d $dir ]
	then
		return 1
	fi	
	
	arrFileName=(`ls $dir`) 

	fileCount=${#arrFileName[@]}
	

	
	if [ $fileCount -gt 0 ]
	then
		echo  $dir "exists and has content."
		askRmContent "$dir" "$default"
		return $?
	fi
	
	return 1
}

function askRmDirIfExist {

if [ $# -lt 2 ]; then
	echo "invalid parameters for askRmDirIfExist dir default[=y/n]"
	exit
fi

	dir=$1
	default=$2
	
	if [ ! -d $dir ]
	then
		return 1
	fi	
	
	
	echo  $dir "exists."
	askRmDir "$dir" "$default"
	return $?
	
	
	
}


#return 
#0: dir not created
#1: empty dir
#2: dir not empty
function needEmptyDir {

if [ $# -lt 3 ]; then
	echo "invalid parameters for needEmptyDir defaultRmDirContent[=y/n] defaultMkDir[=y/n]"
	exit
fi

	dir=$1
	defaultRmDirContent=$2
	defaultMkDir=$3
	
	askRmDirContentIfExist $dir $defaultRmDirContent
	dirEmpty=$?

	askMkDirIfNotExist $dir $defaultMkDir
	dirExist=$?
	
	if [ $dirExist -eq 0 ]
	then
		return 0
	else
		if [ $dirEmpty -eq 1 ]
		then
			return 1
		else
			return 2
		fi
	fi
}

function requestEmptyDirWithWarning {
	dir=$1
	needEmptyDir $dir Y Y	
	result=$?
	if [ $result -eq 0 ]; then
		#no dir created: unacceptable
		echo "Directory $dir not created: fail. quit"
		exit 0
	else
		if [ $result -eq 2 ]; then
			echo "Warning: using non-Empty dir $dir"
		fi
	fi
}

