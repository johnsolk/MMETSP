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

def delete_file(filename):
	os.remove(filename)
	print "File removed:",newdir+i

def execute(url_data):
	for item in url_data.keys():
        	organism=item[0]
        	seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
		print org_seq_dir
		clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
            		sra=basename(urlparse(url).path)
            		newdir=org_seq_dir+sra+"/"
			filename=newdir+sra
			print filename
	    		if os.path.isfile(filename):
	    			print "File exists:",filename 	
				delete_file(filename)
			

basedir="/mnt/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset_b.csv"
url_data=get_data(datafile)
print url_data
execute(url_data)
