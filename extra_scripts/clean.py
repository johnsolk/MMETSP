import os
import os.path
from os.path import basename
from urllib import urlopen
from urlparse import urlparse
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
from shutil import copyfile
import glob
# custom Lisa module
import clusterfunc


def get_data(thefile):
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
            # check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                # check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data


def delete_file(filename):
    os.remove(filename)
    print "File removed:", filename


def send_to_cluster(basedir,commands,name):
    process_name = "delete"
    module_name_list = ""
    filename = name
    clusterfunc.qsub_file(basedir, process_name, module_name_list, filename, commands)


def execute(basedir, url_data):
    for item in url_data.keys():
        organism = item[0]
        seqtype = item[1]
        org_seq_dir = basedir + organism + "/"
        clusterfunc.check_dir(org_seq_dir)
        url_list = url_data[item]
        for url in url_list:
            sra = basename(urlparse(url).path)
            newdir = org_seq_dir + sra + "/"
            sample = "_".join(item)
            filename = newdir + sra

            ##
            # run this to delete SRA file:
            ##

            if os.path.isfile(filename):
                delete_file(filename)
            else:
                print "Already deleted:", filename

            ##
            # run this to delte original raw reads after trim_qc.py
            ##

            if os.path.isfile(filename+"_1.fastq"):
        		delete_file(filename+"_1.fastq")
            if os.path.isfile(filename+"_2.fastq"):
        		delete_file(filename+"_2.fastq")

    #diginormdir = newdir + "diginorm/"
    #os.chdir(diginormdir)
    #diginorm_delete_files = ["norm.C20k20.ct"]
    # diginorm_delete_files=["norm.C20k20.ct","orphans.fq.gz.keep.abundfilt"]
    #for filename in glob.glob("*.keep"):
    #    diginorm_delete_files.append(filename)
    #for filename in glob.glob("*.abundfilt"):
    #    diginorm_delete_files.append(filename)
    #for filename in glob.glob("*.abundfilt.pe"):
    #    diginorm_delete_files.append(filename)
    #for filename in glob.glob("*.abundfilt.se"):
    #    diginorm_delete_files.append(filename)
    #print diginorm_delete_files
# diginormdir=newdir+"diginorm/"
# os.chdir(diginormdir)
# diginorm_delete_files=["norm.C20k20.ct","orphans.keep.abundfilt.fq.gz"]
# for filename in glob.glob("*.keep"):
#	diginorm_delete_files.append(filename)
# for filename in glob.glob("*.abundfilt"):
#	diginorm_delete_files.append(filename)
# for filename in glob.glob("*.abundfilt.pe*"):
#	diginorm_delete_files.append(filename)
# for filename in glob.glob("*.abundfilt.se"):
#	diginorm_delete_files.append(filename)
# print diginorm_delete_files

##
# run this after assembly.py
# to delete extra files
##

    trinitydir = newdir + "trinity/"
    #os.chdir(trinitydir)
    trinity_out = trinitydir + "trinity_out/"
    trinity_fasta = trinity_out + "Trinity.fasta"
    #new_trinity_fasta = trinitydir + sra + ".Trinity.fasta"
    #trinity_fixed_fasta = trinity_out + sample + ".Trinity.fixed.fa"
    #listoffiles = os.listdir(trinitydir)
    #new_trinity_fixed_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
    #filestodelete = []
    #for filename in listoffiles:
    #    if filename.endswith(".1"):
    #        filestodelete.append(filename)
    #    if filename.endswith(".2"):
    #        filestodelete.append(filename)
    #if os.path.isfile(trinity_fasta):
    #    print "File to be copied:", trinity_fasta
    #    print "New file location:", new_trinity_fasta
    #    copyfile(trinity_fasta, new_trinity_fasta)
        # print "These files will be deleted:",trinity_out
        # shutil.rmtree(trinity_out)
    #if os.path.isfile(trinity_fixed_fasta):
    #    print "File to be copied:", trinity_fixed_fasta
    #    print "New file location", new_trinity_fixed_fasta
    #    copyfile(trinity_fixed_fasta, new_trinity_fixed_fasta)
    # print "These files will be deleted:",filestodelete
    # for i in filestodelete:
    #	delete_file(i)


basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
datafile = "../SraRunInfo_719.csv"
url_data = get_data(datafile)
print url_data
execute(basedir,url_data)
