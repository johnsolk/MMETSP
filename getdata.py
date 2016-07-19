# Lisa J. Cohen
# Lab for Data Intensive Biology, UC Davis
# PI: C. Titus Brown
# transcriptome assembly pipeline
# Marine Microbial Eukaryotic Transcriptome Sequencing Project
# data from Keeling et al. 2014
# http://dx.doi.org/10.1371/journal.pbio.1001889


from doit.tools import run_once
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
import mmetsp


def download(url,newdir,newfile):
    	filestring=newdir+newfile
    	urlstring="wget -O "+filestring+" "+url
    
	#Note: for Python 3
    	#urllib.request.urlretrieve(url,filestring)
    
	#s=subprocess.Popen(urlstring,shell=True)
    	#s.wait()
    
	return urlstring,filestring
    
def sra_extract(newdir,filename):
	
    	# checks whether paired end or single end sequencing
	#if seqtype=="single":
    	#    sra_string="fastq-dump -v "+newdir+file
    	#    print sra_string
    	#elif seqtype=="paired":
	
	fastq_file = newdir+"*.fastq"	
	
	sra_string="fastq-dump -v -O "+newdir+" --split-3 "+newdir+filename
			
	#s=subprocess.Popen(sra_string,shell=True,stdout=PIPE)
    	#s.wait()

	return sra_string,fastq_file
		
def fastqc_report(fastq_file_list,newdir,fastqcdir,filename):
	"""
	Generates a fastqc report from all fastq files in the directory 
	imports list of files in each directory
	"""

    	file_string=str(fastq_file_list)
    	file_string=" ".join(fastq_file_list)
    	fastqc_string="fastqc -o "+fastqcdir+" "+file_string
    	
	#s=subprocess.Popen(fastqc_string,shell=True)
    	#s.wait()

	fastqc_report_file = fastqcdir+filename+"_*_fastqc.zip"
	return fastqc_string,fastqc_report_file

def fastqc(newdir,fastqcdir,filename):
        listoffiles=os.listdir(newdir)
        fastq_file_list=[]
        for i in listoffiles:
                if i.endswith(".fastq"):
                        fastq_file_list.append(newdir+i)
        fastqc_string,fastqc_report_file = fastqc_report(fastq_file_list,newdir,fastqcdir,filename)
	return fastqc_string,fastqc_report_file


def execute(basedir,url_data):
	'''Creates directory for each file to be downloaded.
        
	Directory will be located according to organism and read type (single or paired)
	'''
	for item in url_data.keys():
        	organism=item[0]
        	seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
		clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
            		filename=basename(urlparse(url).path)
            		newdir=org_seq_dir+filename+"/"
            		clusterfunc.check_dir(newdir)
	    		fastqcdir=newdir+"fastqc/"
	    		clusterfunc.check_dir(fastqcdir)
            
	       		# 1. Download
			download_command,sra_file = download(url,newdir,filename)
            		task_download_data(download_command,sra_file)
			# 2. Extract
			fastq_dump_command,fastq_file = sra_extract(newdir,filename)
            		task_extract_sra(fastq_dump_command,fastq_file)
			# 3. fastqc report
			fastqc_command,fastqc_report_file = fastqc(newdir,fastqcdir,filename)
			task_fastqc_report(fastqc_command,fastqc_report_file)

def task_download_data(download_command,sra_file):
	
	def download(url,newdir,newfile):
        	filestring=newdir+newfile
        	urlstring="wget -O "+filestring+" "+url

        	#Note: for Python 3
        	#urllib.request.urlretrieve(url,filestring)

	return {'actions':[urlstring],
		'targets':[sra_file],
		'uptodate':[run_once]}

def task_extract_sra(fastq_dump_command,fastq_file):
	return {'actions':[fastq_dump_command],
		'targets':[fastq_file],
		'uptodate':[run_once]}

def task_fastqc_report(fastqc_command,fastqc_report_file):
	return {'actions':[fastqc_command],
		'targets':[fastqc_report_file],
		'uptodate':[run_once]}

datafile="MMETSP_SRA_Run_Info_subset_h.csv"
basedir="/mnt/mmetsp/"
clusterfunc.check_dir(basedir)
url_data=mmetsp.get_data(datafile)
print url_data
execute(basedir,url_data)

