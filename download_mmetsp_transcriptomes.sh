#!/bin/bash

# from Luiz Irber
# sudo apt-get install parallel

seq -w 000 147 | parallel -t -j 5 "wget --spider -r \\
ftp://ftp.imicrobe.us/projects/104/transcriptomes/MMETSP{} 2>&1 \\
| grep --line-buffered -o -E 'ftp\:\/\/.*\.cds\.fa\.gz' > urls{}.txt"
cat urls* | sort -u > download.txt
cat download.txt | parallel -j 30 -t "wget -c {}"

