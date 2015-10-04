Tutorial for downloading and working with MMETSP data:
======================================================
1. Launch AWS instance
2. Install stuff: sudo apt-get sratoolkit, dos2unix, fastqc, default-jre
3. manually install sra-toolkig, tar -xvzf
4. rsync .csv file from SRA (screenshot for how to do this)

rsync -e "ssh -i [key].pem" -avz [source directory] [user]@[instance ip]:[destination directory on instance]

5. dos2unix -c Mac mac_file
6. do stuff
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
