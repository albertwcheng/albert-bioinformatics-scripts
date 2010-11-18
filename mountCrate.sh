
wcl=`ls -l /mit/awcheng/crate-01/awcheng 2> /dev/null | wc -l`

if [ $wcl -lt 1 ]; then
sshfs awcheng@coyote:/net/crate-01/data/burge-stuff/ /mit/awcheng/crate-01
gnome-open /mit/awcheng/crate-01/awcheng
else
echo "Already Mounted at /mit/awcheng/crate-01/"
fi
