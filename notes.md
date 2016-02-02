
References:
  
  * https://github.com/dib-lab/khmer-protocols/blob/jem-streaming/mrnaseq/1-quality.rst
  * https://github.com/dib-lab/khmer-protocols/blob/jem-streaming/mrnaseq/2-diginorm.rst
  * https://github.com/dib-lab/dib-lab/issues/45#issuecomment-139825302
  * https://khmer-protocols.readthedocs.org/en/ctb/mrnaseq/1-quality.html
  * http://khmer.readthedocs.org/en/v2.0/user/scripts.html

Install:

    sudo apt-get update && \
    sudo apt-get -y install screen git curl gcc make g++ python-dev unzip \
          default-jre pkg-config libncurses5-dev r-base-core r-cran-gplots \
          python-matplotlib python-pip python-virtualenv sysstat fastqc \
          trimmomatic bowtie samtools blast2


    git clone https://github.com/ljcohen/MMETSP.git
    cd MMETSP


