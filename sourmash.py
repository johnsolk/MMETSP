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

#1. Get data from spreadsheet

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


def get_sourmash_command(SRA,trinitydir):
	filename=SRA+".left.fq"
	full_filename=trinitydir+filename
	if os.path.isfile(full_filename):
		if os.stat(full_filename).st_size!=0:
			#sourmash_command="""
#head -4000000 {} > /mnt/scratch/ljcohen/mmetsp_tmp/{}.head
#""".format(full_filename,filename)
			sourmash_command="""
sourmash compute --protein -k 18,21 -f /mnt/scratch/ljcohen/mmetsp_tmp/{}.head
""".format(filename)
			#s=subprocess.Popen(sourmash_command,shell=True)
                        #s.wait()
			commands=[sourmash_command]
        		process_name="sourmash"
        		module_name_list=[""]
        		filename=SRA
        		clusterfunc.qsub_file("/mnt/scratch/ljcohen/mmetsp_tmp/",process_name,module_name_list,filename,commands)	
		else:
			print "File is empty:",filename

def execute(basedir,url_data):
	for item in url_data.keys():
        	organism=item[0]
        	org_seq_dir=basedir+organism+"/"
        	url_list=url_data[item]
        	for url in url_list:
            		SRA=basename(urlparse(url).path)
            		newdir=org_seq_dir+SRA+"/"
			trinitydir=newdir+"trinity/"
			get_sourmash_command(SRA,trinitydir)
			#s=subprocess.Popen(sourmash_command,shell=True)
    			#s.wait()
			#if os.path.isfile("*.sig"):
			#	print os.path.listdir(trimdir)
			#else:
			#	print "sourmash not run yet"
				


basedir="/mnt/scratch/ljcohen/mmetsp/"
# The following dictionary is formatted as
# basedir:datafile
#file_locations={"/mnt2/mmetsp/":"MMETSP_SRA_Run_Info_subset_d.csv",
#		"/mnt3/mmetsp/":"MMETSP_SRA_Run_Info_subset_a.csv",
#		"/mnt4/mmetsp/":"MMETSP_SRA_Run_Info_subset_b.csv"}
datafile="SraRunInfo.csv"
mmetsp_data=get_data(datafile)
print mmetsp_data
execute(basedir,mmetsp_data)

