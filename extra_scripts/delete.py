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


def execute(basedir,count):
	listofdirs = os.listdir(basedir)
	for mmetsp  in listofdirs:
		newdir = basedir  + mmetsp + "/"
    		trinitydir = newdir + "trinity/"
    		trinity_out = trinitydir + "trinity_out_2.2.0/"
    		# trinity 2014 version
		#trinity_fasta = trinity_out + "Trinity.fasta"
    		# trinity_2.2.0
		trinity_fasta = trinitydir + "trinity_out_2.2.0.Trinity.fasta"
		if os.path.isdir(trinity_out):
			if os.path.isfile(trinity_fasta):
				if os.stat(trinity_fasta).st_size == 0:
					print cp_string
					print "File is empty:", trinity_fasta
				else:
					print "Directory will be deleted:",trinity_out
					delete_trinity_dir = ["rm -rf "+trinity_out]
					send_to_cluster(basedir,delete_trinity_dir,mmetsp)
					count += 1
			else:
				"Trinity fasta does not exist yet."
		else:
			print "Doesn't exist:",trinity_out
	
	print "Deleted:"
	print count
	


basedir = "/mnt/scratch/ljcohen/mmetsp/"				
#basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
datafile = "../SraRunInfo_719.csv"
#url_data = get_data(datafile)
#print url_data
count = 0
execute(basedir,count)
