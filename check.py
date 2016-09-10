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


def get_data(thefile):
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
        #print headerline        
        position_name=headerline.index("ScientificName")
        position_reads=headerline.index("Run")
        position_ftp=headerline.index("download_path")
        for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            read_type=line_data[position_reads]
            ftp=line_data[position_ftp]
            name_read_tuple=(name,read_type)
            print name_read_tuple
            #check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                #check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def check_empty(empty_files,file,sra):
	if os.stat(file).st_size == 0:
        	print "File is empty:",file
        	if sra not in empty_files:
                	empty_files.append(sra)
	return empty_files

def check_trinity(trinity_fail,trinity_file,sra):
	if os.path.isfile(trinity_file):
        	print "Trinity completed successfully:",trinity_file
        else:
                print "Trinity needs to be run again:",filename
                trinity_fail.append(sra)
	return trinity_fail

def execute(url_data):
	trinity_fail=[]
	empty_files=[]
	for item in url_data.keys():
        	organism=item[0]
        	seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
		clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
            		sra=basename(urlparse(url).path)
            		newdir=org_seq_dir+sra+"/"
			filename=newdir+sra
			## check if trinity exists
			trinitydir=newdir+"trinity/"
			left=trinitydir+"left.fq"
			right=trinitydir+"right.fq"
			empty_files=check(empty_files,left,sra)
			empty_files=check(empty_files,right,sra)
			trinity_outputdir=trinitydir+"trinity_out/"
			trinity_file=trinity_outputdir+"Trinity.fasta"
			trinity_fail=check_trinity(trinity_fail,trinity_file,sra)
			diginormdir=newdir+"diginorm/"
			trimdir=newdir+"trim/"
	print "List of empty files:"
	print empty_files
	print "Trinity needs to be run again:"
	print trinity_fail


basedir="/mnt/scratch/ljcohen/mmetsp/"
datafile="SraRunInfo.csv"
url_data=get_data(datafile)
print url_data
execute(url_data)
