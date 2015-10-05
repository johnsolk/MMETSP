Tutorial for downloading and working with MMETSP data:
======================================================

This tutorial will (eventually) describe steps to get from blank AWS instance, download MMETSP data, quality check and automate eel pond mRNAseq differential expression protocol: https://khmer-protocols.readthedocs.org/en/v0.8.4/mrnaseq/

1. Launch AWS instance
2. Install stuff: sudo apt-get sratoolkit, dos2unix, fastqc, default-jre
3. manually install sra-toolkit, tar -xvzf from http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software
4. rsync .csv file from SRA (screenshot for how to do this) http://www.ncbi.nlm.nih.gov/sra?linkname=bioproject_sra_all&from_uid=231566

rsync -e "ssh -i [key].pem" -avz [source directory] [user]@[instance ip]:[destination directory on instance]

5. dos2unix -c Mac mac_file
6. run getdata.py
7. literate resting, eel-pond: https://github.com/dib-lab/literate-resting/blob/master/kp/eel-pond.rst


References:
http://www.bioinformatics.babraham.ac.uk/projects/fastqc/INSTALL.txt
http://superuser.com/questions/687074/is-there-a-mac2unix-utility
https://community.hpcloud.com/article/using-rsync-upload-or-transfer-files-linux-and-mac-osx
http://www.bioinformatics.babraham.ac.uk/projects/fastqc/INSTALL.txt
http://askubuntu.com/questions/25347/what-command-do-i-need-to-unzip-extract-a-tar-gz-file

vi tricks for editing files:
http://www.lagmonster.org/docs/vi2.html

current version of sra-toolkit is required:
http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=toolkit_doc&f=std
otherwise this error will happen:
http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=toolkit_doc&f=std
