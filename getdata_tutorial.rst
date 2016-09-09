Tutorial for downloading and working with MMETSP data:
======================================================

This tutorial describes steps to get from blank AWS instance, download MMETSP data, quality check and automate eel pond mRNAseq differential expression protocol: 

https://khmer-protocols.readthedocs.org/en/v0.8.4/mrnaseq/

Have used Matt McManes' angus tutorial for some of this:

http://angus.readthedocs.org/en/2015/MacManesTrimming.html


1. Launch AWS instance:

ssh -i mmetsp.pem ubuntu@ec2-52-91-248-80.compute-1.amazonaws.com

2. Install stuff: 

.. code::

  sudo bash
  apt-get update
  apt-get upgrade
  
  apt-get -y install screen git curl gcc dos2unix fastqc default-jre \
  make python-pip g++ python-dev unzip build-essential libcurl4-openssl-dev \
  zlib1g-dev pkg-config libncurses5-dev r-cran-gplots python-virtualenv sysstat \
  samtools bowtie trimmomatic blast2 r-base-core python-matplotlib python-pip fastqc \
  ruby hmmer unzip infernal ncbi-blast+ liburi-escape-xs-perl emboss liburi-perl \
  libsm6 libxrender1 libfontconfig1 parallel transdecoder last-align
  pip install --upgrade pip
  
  curl -OL https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.4.0-Linux-x86_64.sh
  bash Anaconda2-2.4.0-Linux-x86_64.sh
  source ~/.bashrc
  conda update pandas numexpr
  sudo pip install -U setuptools
  sudo pip install dammit
  sudo gem install crb-blast
  split-paired-reads.py
  

Install Trimmomatic:

.. code::
  
  cd ~/bin
  wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.33.zip
  unzip Trimmomatic-0.33.zip
  cd Trimmomatic-0.33
  chmod +x trimmomatic-0.33.jar

Install libgtextutils and fastx:

.. code::

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

.. code::

  df -h
  mkfs -t ext4 /dev/xvdb
  mount /dev/xvdb /mnt
  chown -R ubuntu:ubuntu /mnt
  df -h


3. Download latest version of sra-toolkit for linux Ubuntu 64-bit architecture from here: http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software

.. code::
  
  cd
  curl -O http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.5.4-1/sratoolkit.2.5.4-1-ubuntu64.tar.gz
  tar -xvzf sratoolkit.2.5.4-1-ubuntu64.tar.gz
  echo 'export PATH=$PATH:/home/ubuntu/sratoolkit.2.5.4-1-ubuntu64/bin' >> ~/.bashrc
  source ~/.bashrc

4. Make .csv spreadsheet file from SRA (screenshot for how to do this): http://www.ncbi.nlm.nih.gov/sra?linkname=bioproject_sra_all&from_uid=231566

Click on "Send to:" -> Choose Destination: File -> "Download 719 items." Format: (pull down) Accession -> Click on "Create File"

This will download to your local computer. Then rsync or upload from local to AWS instance:

.. code::

  rsync -e "ssh -i [key].pem" -avz [source directory] [user]@[instance ip]:[destination directory on instance]


5. login to AWS
6. 

.. code::
  
  mkdir ~/mmetsp
  cd ~/mmetsp
  git init
  git pull https://github.com/ljcohen/MMETSP.git
  dos2unix MMETSP_SRA_Run_Info_subset.csv
  chmod 666 *.*


7. run: 

.. code::

  python getdata.py:


- gets url for each sample from spreadsheet
- creates directory for that sample according to Scientific name
- downloads sra file into that directory
- extracts the file from sra to .fastq
- Makes subset of reads to test, 40k each (only use this during testing of the pipeline)
- creates a link to data into a working directory

8. The Supplementary Materials and methods section of the Keeling et al. 2014 paper indicates all sequencing was paired-end Illumina with TruSq RNA Sample Preparation Kit with fragment sizes ranging from 240 to 350 pb. Some was PE-50 and some were PE-100. While we don't know specifically which Illumina adapters were used , we will use a combined file of all TruSeq2 and TruSeq3 adapters with to see. From the trimresults.log file located in this repository, it doesn't seem to matter which adapters to use. So, we will use all of them. 

.. code::

  python trim_qc.py

This will create .sh files for each SRA accession, TruSeq2 and TruSeq3:

To run Trimmomatic with all bash scripts:

.. code::

  apt-get install parallel
  parallel -j0 bash :::: <(ls *.sh)
  
Then run

.. code::

  python trimparse.py > trimresults.log

Trimmomatic creates paired (P) and unpaired (U) files for each read 1 and 2 = 4 files for each SRA. Only choose the P files for the next step to interleave reads. (Note: All Trimmomatic results for this step were >90% reads kept.)

(I know this is a bad idea, but in the interest of getting this to work...) Comment out Trimmomatic function and run this again to interleave reads, then again to run jellyfish:

.. code::
  
  python trim_qc.py

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
