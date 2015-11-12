for file in /mnt/mmetsp/diginorm/*.abundfilt.pe
do
	newfile=${file%%.fq.keep.abundfilt.pe}.keep.abundfilt.fq
	mv ${file} ${newfile}
	gzip ${newfile}
done
