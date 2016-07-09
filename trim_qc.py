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
	listoffile = os.listdir(trimdir)
	#print listoffile
	trim_file = trimdir+"trim."+sra+".log"
	#print trim_file
	matching = [s for s in listoffile if "trim."+sra+".log" in s]
	matching_string = "TrimmomaticPE: Completed successfully"
	with open(trim_file) as f:
    		content = f.readlines()
	if len(matching)!=0:
		trim_complete = [m for m in content if matching_string in m]
		if len(trim_complete)!=0:
			print "Already trimmed:",matching
		else:
			j="""#!/bin/bash
java -jar /mnt/home/ljcohen/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.trim.fq \\
{} {} \\
ILLUMINACLIP:/mnt/home/ljcohen/bin/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
			orphan_string=make_orphans(trimdir,sra)
			os.chdir(trimdir)	
			with open(bash_filename,"w") as bash_file:
				bash_file.write(j)
				bash_file.write(orphan_string)
			print "Trimming with Trimmomatic now..."
			s=subprocess.Popen("bash "+bash_filename,shell=True)
    			s.wait()
    			print "Trimmomatic completed."
    			os.chdir("/mnt/home/ljcohen/MMETSP/")

def make_orphans(trimdir,sra):
    #if os.path.isfile(trimdir+"orphans.fq.gz"):
	#if os.stat(trimdir+"orphans.fq.gz").st_size != 0:
	#	print "orphans file exists:",trimdir+"orphans.fq.gz"
    	#else:
	#	print "orphans file exists but is empty:",trimdir+"orphans.fq.gz"
    #else:
    	file1 = sra+".trim_1U.fq"
	file2 = sra+".trim_2U.fq"
	orphanlist=file1 + " " + file2
    	orphan_string="gzip -9c "+orphanlist+" > "+trimdir+"orphans.fq.gz"
    	print orphan_string
    	#s=subprocess.Popen(orphan_string,shell=True)
    	#s.wait()
	return orphan_string

def interleave_reads(trimdir,sra,interleavedir):
    interleavefile=interleavedir+sra+".trimmed.interleaved.fq"
    if os.path.isfile(interleavefile):
	print "already interleaved"
    else:
    	interleave_string="interleave-reads.py "+trimdir+sra+".trim_1P.fq "+trimdir+sra+".trim_2P.fq > "+interleavefile
    	print interleave_string
	print "Interleaving now..."
    	#s=subprocess.Popen(interleave_string,shell=True)    
    	#s.wait()
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
		clusterfunc.check_dir(trimdir)
		interleavedir=newdir+"interleave/"
		clusterfunc.check_dir(interleavedir)
		file1=newdir+sra+"_1.fastq"
		file2=newdir+sra+"_2.fastq"
		if os.path.isfile(file1) and os.path.isfile(file2):
			print file1
			print file2
		run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
		#interleave_reads(trimdir,sra,interleavedir)
		#make_orphans(trimdir)
		#else:
		#	print "Files do not exist:",file1,file2 	


datafile="MMETSP_SRA_Run_Info_subset_msu1.csv"
datadir="/mnt/scratch/ljcohen/mmetsp/"
url_data=get_data(datafile)
print url_data
execute(url_data,datadir)



