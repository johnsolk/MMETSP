gzip -9c /mnt/mmetsp/diginorm/orphans.fq.gz.keep.abundfilt > /mnt/mmetsp/diginorm/orphans.keep.abundfilt.fq.gz && \
	rm /mnt/mmetsp/diginorm/orphans.fq.gz.keep.abundfilt
for file in /mnt/mmetsp/diginorm/*.se
do
	gzip -9c ${file} >> orphans.keep.abundfilt.fq.gz && \
		rm ${file}
done
