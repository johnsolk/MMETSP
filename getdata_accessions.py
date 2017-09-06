import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import glob
# custom Lisa module
import clusterfunc_py3

# 1. Get url for download from list of accessions

def sra_url(accession):
    """
    Takes an SRA accession and determines the location of the .sra data file for automated or downloading.
    Follows this format: ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra/{SRR|ERR|DRR}/<first 6 characters of accession>/<accession>/<accession>.sra
    Format according to NCBI utility handbook: https://www.ncbi.nlm.nih.gov/books/NBK158899/
    """
    accession = accession.upper()
    return "ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra/{}/{}/{}/{}.sra".format(
           accession[0:3], accession[0:6], accession, accession)

def test_sra_url():
    assert sra_url('DRR053698') == 'ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByRun/sra/DRR/DRR053/DRR053698/DRR053698.sra'

# 2. Download data
#(already checked if file exists)


def download(url, newdir, newfile):
    filestring = newdir + newfile
    if os.path.isfile(filestring):
        print("file exists:", filestring)
    else:
        urlstring = "wget -O " + newdir + newfile + " " + url
        print(urlstring)
    #s = subprocess.Popen(urlstring, shell=True)
    #s.wait()

    print("Finished downloading from NCBI.")

# 3. Extract with fastq-dump (sratools)


def sra_extract(newdir, filename):
    # if seqtype=="single":
    #    sra_string="fastq-dump -v "+newdir+file
    #    print sra_string
    # elif seqtype=="paired":
        # check whether .fastq exists in directory
    if glob.glob(newdir + "*.fastq"):
        print("SRA has already been extracted", filename)
    else:
        sra_string = "fastq-dump -v -O " + newdir + " --split-3 " + newdir + filename
        print(sra_string)
        print("extracting SRA...")
        #s = subprocess.Popen(sra_string, shell=True, stdout=PIPE)
        #s.wait()
        print("Finished SRA extraction.")

# 4. Generate fastqc from all fastq in directory


def fastqc_report(fastq_file_list, newdir, fastqcdir, filename):
    # imports list of files in each directory
    print(fastq_file_list)
    print(fastqcdir + filename)
    if glob.glob(fastqcdir + filename + "_*_fastqc.zip"):
        print("fastqc already complete:", filename)
    else:
        # creates command to generate fastqc reports from all files in list
        file_string = str(fastq_file_list)
    # print fastq_file_list
        file_string = " ".join(fastq_file_list)
    # print file_string
        fastqc_string = "fastqc -o " + fastqcdir + " " + file_string
    print("fastqc reports being generated for: " + str(fastq_file_list))
    fastqc_command = [fastqc_string]
    process_name = "fastqc"
    module_name_list = ""
    filename = filename
    clusterfunc_py3.qsub_file(fastqcdir, process_name,
                          module_name_list, filename, fastqc_command)

# this is the main function to execute


def execute(accession, basedir, url):
        # Creates directory for each file to be downloaded
        # Directory will be located according to organism and read type (single
        # or paired)
    seq_dir = basedir + accession + "/"    
    clusterfunc_py3.check_dir(seq_dir)
    print(seq_dir)
    fastqcdir = seq_dir + "fastqc/"
    clusterfunc_py3.check_dir(fastqcdir)
    filename = accession + ".sra"
    if filename in os.listdir(seq_dir):
        print("sra exists:", filename)
        if os.stat(seq_dir + filename).st_size == 0:
            print("SRA file is empty:", filename)
            os.remove(full_filename)
    else:
        print("file will be downloaded:", filename)
        download(url, seq_dir, filename)
        sra_extract(seq_dir, filename)
    fastqc(seq_dir, fastqcdir, filename)

def fastqc(newdir, fastqcdir, filename):
    listoffiles = os.listdir(newdir)
    print(listoffiles)
    fastq_file_list = []
    for i in listoffiles:
        if i.endswith(".fastq"):
            fastq_file_list.append(newdir + i)
    fastqc_report(fastq_file_list, newdir, fastqcdir, filename)

accessions = "DRR053698, DRR082659, ERR489297, DRR030368, DRR031870, DRR046632, DRR069093, ERR058009, ERR1016675, SRR2086412, SRR3499127, SRR1789336, SRR2016923, ERR1674585, DRR036858"
accessions = accessions.replace(" ","").split(",")
print(accessions)
basedir = "/mnt/scratch/ljcohen/oysterriver/"
clusterfunc_py3.check_dir(basedir)
for accession in accessions:
   url = sra_url(accession)
   execute(accession,basedir,url)
#print url_data
#execute(basedir, url_data)
