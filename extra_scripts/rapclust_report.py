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
import yaml
# custom Lisa module
import clusterfunc

def get_data(thefile):
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
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
            if name_read_tuple in url_data.keys():
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def get_read_numbers(salmondir,sra):
	salmondir_quant = salmondir+sra+".quant/"
	read_count="cat "+salmondir_quant+"quant.sf | wc -l"
	print salmondir
	print read_count
	s=subprocess.Popen(read_count,shell=True)
        s.wait()

def get_clusters(salmondir,rapclustdir,sra):
	out_dir=rapclustdir+sra+"_rapclust_out/"
	cluster_num="cat "+out_dir+"mag.clust | wc -l"
	print rapclustdir
	print cluster_num
	s=subprocess.Popen(cluster_num,shell=True)
        s.wait()

def execute(url_data):
        for item in url_data.keys():
                organism=item[0]
                org_seq_dir=basedir+organism+"/"
                url_list=url_data[item]
                for url in url_list:
                        sra=basename(urlparse(url).path)
                        newdir=org_seq_dir+sra+"/"
                        salmondir=newdir+"salmon/"
			rapclustdir=newdir+"rapclust/"
			clusterfunc.check_dir(rapclustdir)
                        clusterfunc.check_dir(salmondir)
			get_read_numbers(salmondir,sra)
			get_clusters(salmondir,rapclustdir,sra)

basedir="/mnt/scratch/ljcohen/mmetsp/"
datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
        "MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]
for datafile in datafiles:
        url_data=get_data(datafile)
        print url_data
        execute(url_data)
