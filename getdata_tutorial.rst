Tutorial for downloading and working with MMETSP data:
======================================================

This tutorial describes steps to get from blank AWS instance, download MMETSP data, quality check and automate eel pond mRNAseq differential expression protocol: 

https://khmer-protocols.readthedocs.org/en/v0.8.4/mrnaseq/

1. Launch AWS instance:

ssh -i mmetsp.pem ubuntu@ec2-52-91-248-80.compute-1.amazonaws.com

2. Install stuff: 

.. code::
  sudo bash
  apt-get install dos2unix fastqc default-jre

Install screed:

.. code::

  cd /usr/local/share
  git clone https://github.com/ged-lab/screed.git
  cd screed
  git checkout protocols-v0.8.3
  python setup.py install`

Install khmer:

.. code::
  cd /usr/local/share
  git clone https://github.com/dib-lab/khmer.git
  cd khmer
  git checkout protocols-v0.8.3
  make
  echo 'export PYTHONPATH=$PYTHONPATH:/usr/local/share/khmer' >> ~/.bashrc
  source ~/.bashrc

Install Trimmomatic:

.. code:
  
  cd ~/bin
  wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.33.zip
  unzip Trimmomatic-0.33.zip
  cd Trimmomatic-0.33
  chmod +x trimmomatic-0.33.jar

Install libgtextutils and fastx:

.. code:
  cd /root
  curl -O http://hannonlab.cshl.edu/fastx_toolkit/libgtextutils-0.6.1.tar.bz2
  tar xjf libgtextutils-0.6.1.tar.bz2
  cd libgtextutils-0.6.1/
  ./configure && make && make install

  cd /root
  curl -O http://hannonlab.cshl.edu/fastx_toolkit/fastx_toolkit-0.0.13.2.tar.bz2
  tar xjf fastx_toolkit-0.0.13.2.tar.bz2
  cd fastx_toolkit-0.0.13.2/
  ./configure && make && make install

Mount hard drive

.. code:
  df -h
  mkfs -t ext4 /dev/xvdb
  mount /dev/xvdb /mnt
  chown -R ubuntu:ubuntu /mnt
  df -h


3. Download latest version of sra-toolkit for linux Ubuntu 64-bit architecture from here: http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software

.. code::
  
  curl -O http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.5.4-1/sratoolkit.2.5.4-1-ubuntu64.tar.gz
  tar -xvzf sratoolkit.2.5.4-1-ubuntu64.tar.gz

4. Make .csv spreadsheet file from SRA (screenshot for how to do this): http://www.ncbi.nlm.nih.gov/sra?linkname=bioproject_sra_all&from_uid=231566

Click on "Send to:" -> Choose Destination: File -> "Download 719 items." Format: (pull down) Accession -> Click on "Create File"

This will download to your local computer. Then rsync or upload from local to AWS instance:

.. code::
  rsync -e "ssh -i [key].pem" -avz [source directory] [user]@[instance ip]:[destination directory on instance]


5. login to AWS
6. dos2unix -c Mac mac_file
7. run getdata.py:

- gets url for each sample from spreadsheet
- creates directory for that sample according to Scientific name
- downloads sra file into that directory
- extracts the file from sra to .fastq
- (During testing of this pipeline, don't use the whole data set! It's too big. (~1TB). Instead, use subset of 12 samples and create new data files with only 400,000 reads each.)
- creates a link to data into a working directory



8. The Supplementary Materials and methods section of the Keeling et al. 2014 paper indicates all sequencing was paired-end Illumina with TruSq RNA Sample Preparation Kit with fragment sizes ranging from 240 to 350 pb. Some was PE-50 and some were PE-100. While we don't know specifically which Illumina adapters were used nor which chemistry v1,2,3,4 was used, we will use v2 and v3 files from Trimmomatic to see.

.. code:

  mkdir trim
  cd trim

Run trimming levels Phred=30 with current version of Trimmomatic:

http://angus.readthedocs.org/en/2015/MacManesTrimming.html

.. code:

  java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \
  -threads 8 -baseout "+filename+".TruSeq3.Phred30.fq \
  /mnt/reads/root_S13.R1.fq \
  /mnt/reads/root_S13.R2.fq \
  ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq3-PE.fa:2:30:10 \
  SLIDINGWINDOW:4:30 \
  LEADING:30 \
  TRAILING:30 \
  MINLEN:25

Then try other TruSeq adapters:

.. code:

  java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \
  -threads 8 -baseout "+filename+".TruSeq2.Phred30.fq \
  /mnt/reads/root_S13.R1.fq \
  /mnt/reads/root_S13.R2.fq \
  ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq2-PE.fa:2:30:10 \
  SLIDINGWINDOW:4:30 \
  LEADING:30 \
  TRAILING:30 \
  MINLEN:25

References:

literate resting, eel-pond: https://github.com/dib-lab/literate-resting/blob/master/kp/eel-pond.rst


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
