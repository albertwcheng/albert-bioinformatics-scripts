cd /net/coldfact/data/.Trash-awcheng
ls
echo "changing mode"
chmod -R 777 *
for i in *; do
	echo "removing $i"
	rm -f -R "$i"
done
