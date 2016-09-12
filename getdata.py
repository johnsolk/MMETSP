# review comments

import os
import os.path
from os.path import basename
from urllib import urlopen
from urlparse import urlparse
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
import glob
# custom Lisa module
import clusterfunc
# in argparse, execute:
# clusterfunc.set_DO_QSUB(True) when debug flag is set

# 1. Get data from spreadsheet

# in other files, use this as a module, then use "from getdata import get_data"
# consider changing your naming conventions

def get_data(thefile):
    # use csv module in the for loop
    count = 0
    url_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_ftp = headerline.index("download_path")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            ftp = line_data[position_ftp]
            name_read_tuple = (name, read_type)
            print name_read_tuple
            # check if name_read_tuple exist, if not then add empty set and add ftp
            value = url_data.get(name_read_tuple, set())
            value.add(ftp)
            url_data[name_read_tuple] = value
        return url_data

# 2. Download data
#(already checked if file exists)


def download(url, newdir, newfile):
    filestring = newdir + newfile
    if os.path.isfile(filestring):
        print "file exists:", filestring
    else:
        urlstring = "wget -O " + newdir + newfile + " " + url
        print urlstring
    s = subprocess.Popen(urlstring, shell=True)
    s.wait()

    print "Finished downloading from NCBI."

# 3. Extract with fastq-dump (sratools)


def sra_extract(newdir, filename):
    # if seqtype=="single":
    #    sra_string="fastq-dump -v "+newdir+file
    #    print sra_string
    # elif seqtype=="paired":
        # check whether .fastq exists in directory
    
    
    # never use this type of concatenation with path names
    # use glob.glob(os.path.join(newdir,"*.fastq))
    # predict filename more specifically
    # check md5sum?
    if glob.glob(newdir + "*.fastq"):
        print "SRA has already been extracted", filename
    else:
        sra_string = "fastq-dump -v -O " + newdir + " --split-3 " + newdir + filename
        print sra_string
        print "extracting SRA..."
        s = subprocess.Popen(sra_string, shell=True, stdout=PIPE)
        s.wait()
        print "Finished SRA extraction."

# 4. Generate fastqc from all fastq in directory


def fastqc_report(fastq_file_list, newdir, fastqcdir, filename):
    # imports list of files in each directory
    print fastq_file_list
    print fastqcdir + filename
    if glob.glob(fastqcdir + filename + "_*_fastqc.zip"):
        print "fastqc already complete:", filename
    else:
        # creates command to generate fastqc reports from all files in list
        
        # find out if this is necessary
        file_string = str(fastq_file_list)
        
    # print fastq_file_list
        file_string = " ".join(fastq_file_list)
    # print file_string
        fastqc_string = "fastqc -o " + fastqcdir + " " + file_string
    print "fastqc reports being generated for: " + str(fastq_file_list)
    fastqc_command = [fastqc_string]
    process_name = "fastqc"
    module_name_list = ""
    filename = filename
    clusterfunc.qsub_file(fastqcdir, process_name,
                          module_name_list, filename, fastqc_command)

# this is the main function to execute


def execute(basedir, url_data):
    for item in url_data.keys():
        # Creates directory for each file to be downloaded
        # Directory will be located according to organism and read type (single
        # or paired)
        organism = item[0]
        seqtype = item[1]
        org_seq_dir = basedir + organism + "/"
        print org_seq_dir
        clusterfunc.check_dir(org_seq_dir)
        url_list = url_data[item]
        for url in url_list:
            filename = basename(urlparse(url).path)
            print filename
            newdir = org_seq_dir + filename + "/"
            full_filename = newdir + filename
            clusterfunc.check_dir(newdir)
            fastqcdir = newdir + "fastqc/"
            clusterfunc.check_dir(fastqcdir)
            # check to see if filename exists in newdir
            if filename in os.listdir(newdir):
                print "sra exists:", filename
                if os.stat(full_filename).st_size == 0:
                    print "SRA file is empty:", filename
                    os.remove(full_filename)
            else:
                print "file will be downloaded:", filename
                download(url, newdir, filename)
            sra_extract(newdir, filename)
    fastqc(newdir, fastqcdir, filename)

def fastqc(newdir, fastqcdir, filename):
    listoffiles = os.listdir(newdir)
    print listoffiles
    fastq_file_list = []
    for i in listoffiles:
        if i.endswith(".fastq"):
            fastq_file_list.append(newdir + i)
    fastqc_report(fastq_file_list, newdir, fastqcdir, filename)

def main():
    datafile = "SraRunInfo.csv"
    basedir = "/mnt/scratch/ljcohen/mmetsp/"
    clusterfunc.check_dir(basedir)
    for datafile in datafiles:
      url_data = get_data(datafile)
      print url_data
      execute(basedir, url_data)

print __name__
#if __name__ == "__main__":      
#    main()
