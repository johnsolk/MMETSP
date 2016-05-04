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

def salmon_index(salmondir,sra,trinity_fasta):
	index=sra+"_index"
	os.chdir(salmondir)
	if os.path.isfile(trinity_fasta):
		print "file exists:",trinity_fasta
	salmon_index="salmon index --index "+index+" --transcripts "+trinity_fasta+" --type quasi"
	print salmon_index	
	s=subprocess.Popen(salmon_index,shell=True)
	s.wait()
	print "Indexed."
	os.chdir("/home/ubuntu/MMETSP/")
	return index

def quant_salmon(salmondir,index,sra,newdir):
	os.chdir(salmondir)
	file1=newdir+"trinity/left.fq"
	file2=newdir+"trinity/right.fq"
	if os.path.isfile(file1):
		print "file exists:",file1
	if os.path.isfile(file2):
		print "file exists:",file2
	salmon_string="salmon quant -i "+index+" --libType IU -1 "+file1+" -2 "+file2+" -o "+salmondir+sra+".quant"
	os.chdir("/home/ubuntu/MMETSP/")
        s=subprocess.Popen(salmon_string,shell=True)
	s.wait()
	os.chdir("/home/ubuntu/MMETSP/")
	


def gather_counts(salmondir):
	os.chdir(salmondir)
	gather_counts="python /home/ubuntu/MMETSP/gather-counts.py"
	print os.getcwd()
	print gather_counts
	#s=subprocess.Popen(gather_counts,shell=True)
        #s.wait()
	os.chdir("/home/ubuntu/MMETSP/")	

def sim_link(salmondir,sra):
	counts_files_dir="/home/ubuntu/MMETSP/counts/"
	clusterfunc.check_dir(counts_files_dir)
	link_command="ln -fs "+salmondir+"*.counts "+counts_files_dir+sra+".counts" 
	print link_command


def execute(url_data):
	for item in url_data.keys():
		organism=item[0]
		org_seq_dir=basedir+organism+"/"
		url_list=url_data[item]
		for url in url_list:
			sra=basename(urlparse(url).path)
			newdir=org_seq_dir+sra+"/"
			trinitydir=newdir+"trinity/trinity_out/"
			salmondir=newdir+"salmon/"
			clusterfunc.check_dir(salmondir)
			trinity_fasta=trinitydir+"Trinity.fasta"
			#index=salmon_index(salmondir,sra,trinity_fasta)
			#quant_salmon(salmondir,index,sra,newdir)
			#gather_counts(salmondir)		
			sim_link(salmondir,sra)			
	
# The following dictionary is formatted as
# basedir:datafile
file_locations={"/mnt2/mmetsp/":"MMETSP_SRA_Run_Info_subset_d.csv",
                "/mnt3/mmetsp/":"MMETSP_SRA_Run_Info_subset_a.csv",
                "/mnt4/mmetsp/":"MMETSP_SRA_Run_Info_subset_b.csv"}
for basedir in file_locations.keys():
        datafile=file_locations[basedir]
        mmetsp_data=get_data(datafile)
        print mmetsp_data
        execute(mmetsp_data)
