import fnmatch
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

# 1. Get data from spreadsheet


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

def get_head_command(SRA, full_filename, filename):
	head_command="""
head -4000000 {} > /mnt/scratch/ljcohen/mmetsp_sourmash/{}.head
""".format(full_filename,filename)
	commands = [head_command]
	process_name = "head"
	module_name_list = [""]
	filename = SRA
	#clusterfunc.qsub_file("/mnt/scratch/ljcohen/mmetsp_sourmash/",
        #                          process_name, module_name_list, filename, commands)

def get_sourmash_command(SRA, filename):
	sourmash_command="""
sourmash compute -k 21,31 -f /mnt/scratch/ljcohen/mmetsp_sourmash/{}.head
""".format(filename)
        commands = [sourmash_command]
        process_name = "sourmash"
        module_name_list = [""]
        filename = SRA
        clusterfunc.qsub_file("/mnt/scratch/ljcohen/mmetsp_sourmash/",
                                  process_name, module_name_list, filename, commands)

def execute(basedir, url_data):
	count = 0
	failed = 0
	for item in url_data.keys():
        	organism = item[0].replace("'","")
        	org_seq_dir = basedir + organism + "/"
        	url_list = url_data[item]
        	for url in url_list:
    			SRA = basename(urlparse(url).path)
    			newdir = org_seq_dir + SRA + "/"
    			trinitydir = newdir + "trinity/"
			filename = SRA + ".left.fq"
    			full_filename = trinitydir + filename
    			head_file = "/mnt/scratch/ljcohen/mmetsp_sourmash/" + filename + ".head"
			if os.path.isfile(head_file):
				if os.stat(head_file).st_size != 0:
					get_sourmash_command(SRA,filename)
					count += 1
				else:
					print "head command ran, but empty:",head_file
					if os.path.isfile(full_filename):
						if os.stat(full_filename).st_size != 0: 
							head_file = get_head_command(SRA, full_filename, filename)
							count += 1
						else:
							print "File is empty:",full_filename
							failed += 1
					else:
						print "File does not exist:",full_filename
						failed += 1
			else:
				print "head command didn't run:",head_file
				if os.path.isfile(full_filename):
                                        if os.stat(full_filename).st_size != 0: 
                                                head_file = get_head_command(SRA, full_filename, filename)
                                                count += 1
                                        else:
                                                        print "File is empty:",full_filename
                                                        failed += 1
                                else:
                                        print "File does not exist:",full_filename
                                        failed += 1
	print "Sourmash run:",count
	print "Failed:",failed

basedir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "SraRunInfo.csv"
mmetsp_data = get_data(datafile)
print mmetsp_data
execute(basedir, mmetsp_data)
