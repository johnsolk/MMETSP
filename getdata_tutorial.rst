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
  git clone https://github.com/ged-lab/khmer.git
  cd khmer
  git checkout protocols-v0.8.3
  make
  echo 'export PYTHONPATH=$PYTHONPATH:/usr/local/share/khmer' >> ~/.bashrc
  source ~/.bashrc

Install Trimmomatic:

.. code:

  cd /root
  curl -O http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.30.zip
  unzip Trimmomatic-0.30.zip
  cd Trimmomatic-0.30/
  cp trimmomatic-0.30.jar /usr/local/bin
  cp -r adapters /usr/local/share/adapters

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

3. Download latest version of sra-toolkit for linux Ubuntu 64-bit architecture from here: http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software

.. code::
  
  curl -O http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.5.4-1/sratoolkit.2.5.4-1-ubuntu64.tar.gz
  tar -xvzf sratoolkit.2.5.4-1-ubuntu64.tar.gz

4. Make .csv spreadsheet file from SRA (screenshot for how to do this): http://www.ncbi.nlm.nih.gov/sra?linkname=bioproject_sra_all&from_uid=231566

Then rsync from local to AWS instance:

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

8. Find the right Illumina adapters

...




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
