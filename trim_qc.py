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

# run trimmomatic

def run_trimmomatic_TruSeq(trimdir,file1,file2,sra):
  	bash_filename=trimdir+sra+".trim.TruSeq.sh"
    # check for whether this process has been run:
    	listoffiles=os.listdir(trimdir)
	matching = [s for s in listoffiles if "_1P.fq" in s]
	if len(matching)!=0:
		print "Already trimmed:",listoffiles
	else:
		j="""#!/bin/bash
java -Xmx10g -jar /home/ljcohen/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.trim.fq \\
{} {} \\
ILLUMINACLIP:/home/ljcohen/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
		os.chdir(trimdir)
		print j	
		with open(bash_filename,"w") as bash_file:
			bash_file.write(j)
    		print "file written:",bash_filename
    		print "Trimming with Trimmomatic now..."
		s=subprocess.Popen("sudo bash "+bash_filename,shell=True)
    		s.wait()
    		print "Trimmomatic completed."
    		os.chdir("/home/ljcohen/MMETSP/")

def make_orphans(trimdir):
    	if os.path.isfile(trimdir+"orphans.fq.gz"):
		if os.stat(trimdir+"orphans.fq.gz").st_size != 0:
			print "orphans file exists:",trimdir+"orphans.fq.gz"
		else:
			print "orphans file exists but is empty:",trimdir+"orphans.fq.gz"
 	else:
		listoffiles=os.listdir(trimdir)
    		orphanreads=[]
    		for i in listoffiles:
			if i.endswith("_1U.fq"):
				orphanreads.append(trimdir+i)
			elif i.endswith("_2U.fq"):
				orphanreads.append(trimdir+i)
		orphanlist=" ".join(orphanreads)
    		print orphanlist
    		orphan_string="gzip -9c "+orphanlist+" > "+trimdir+"orphans.fq.gz"
    		print orphan_string
    		s=subprocess.Popen(orphan_string,shell=True)
    		s.wait()

def interleave_reads(trimdir,sra,interleavedir):
    	interleavefile=interleavedir+sra+".trimmed.interleaved.fq"
    	if os.path.isfile(interleavefile):
		print "already interleaved"
    	else:
    		interleave_string="interleave-reads.py "+trimdir+sra+".trim_1P.fq "+trimdir+sra+".trim_2P.fq > "+interleavefile
    		print interleave_string
		print "Interleaving now..."
    		s=subprocess.Popen(interleave_string,shell=True)    
    		s.wait()
		print "Reads interleaved."

def execute(url_data,datadir):
    for item in url_data.keys():
	organism=item[0]
	org_seq_dir=datadir+organism+"/"
	url_list=url=url_data[item]
	for url in url_list:
		sra=basename(urlparse(url).path)
		newdir=org_seq_dir+sra+"/"
		trimdir=newdir+"trim/"
		interleavedir=newdir+"interleave/"
		clusterfunc.check_dir(trimdir)
		interleavedir=newdir+"interleave/"
		clusterfunc.check_dir(interleavedir)
		file1=newdir+sra+"_1.fastq"
		file2=newdir+sra+"_2.fastq"
		#if os.path.isfile(file1) and os.path.isfile(file2):
		#	print file1
		#	print file2
		run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
		#interleave_reads(trimdir,sra,interleavedir)
		make_orphans(trimdir)
		#else:
		#	print "Files do not exist:",file1,file2 	

datafile="MMETSP_SRA_Run_Info_subset_jetstream1.csv"
basedir="/vol1/mmetsp/"
clusterfunc.check_dir(basedir)
url_data=get_data(datafile)
print url_data
execute(url_data,basedir)


