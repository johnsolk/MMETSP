for file in /mnt/mmetsp/Micromonas_pusilla/SRR1300457/diginorm/*trimmed.interleaved.fq.keep.abundfilt.pe
do
	newfile=${file%%.fq.keep.abundfilt.pe}.keep.abundfilt.fq
	mv ${file} ${newfile}
	gzip ${newfile}
done
