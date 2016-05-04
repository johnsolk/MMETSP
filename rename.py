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
# Python plotting libraries
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats, integrate
#sns.set(color_codes=True)

def get_data(thefile):
    count=0
    url_data={}
    if os.path.isfile(thefile):
	print "file exists",thefile
    else:
	print os.getcwd()
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

def fix_fasta(trinity_fasta,trinity_dir,sra):
# insert SRR before 


	#os.chdir(trinity_dir)
	trinity_out=trinity_dir+sra+".Trinity.fixed.fa"
	fix="""
sed -e "s/^>/>{}_/" {} | sed 's_|_-_g' | sed "s/\s.*$//" > {}
""".format(sra,trinity_fasta,trinity_out,trinity_out,trinity_out)
	print fix
        s=subprocess.Popen(fix,shell=True)
	s.wait()
	os.chdir("/home/ubuntu/MMETSP/")
	return trinity_out

def execute(url_data):
	for item in url_data.keys():
		organism=item[0]
		org_seq_dir=basedir+organism+"/"
		url_list=url_data[item]
		for url in url_list:
			sra=basename(urlparse(url).path)
			newdir=org_seq_dir+sra+"/"
			trinitydir=newdir+"trinity/trinity_out/"
			clusterfunc.check_dir(trinitydir)
			trinity_fasta=trinitydir+"Trinity.fasta"
			fixed_trinity=fix_fasta(trinity_fasta,trinitydir,sra)


basedir="/mnt/mmetsp/"
datafile="/home/ubuntu/MMETSP/MMETSP_SRA_Run_Info_subset_c.csv"
url_data=get_data(datafile)
print url_data
execute(url_data)
