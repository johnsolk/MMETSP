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

#1. Get data from spreadsheet

def get_data(thefile):
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split('\t')
        position_name=headerline.index("Organism Common Name")
        position_reads=headerline.index("Data Type")
        position_ftp=headerline.index("Download")
        for line in inputfile:
            line_data=line.split('\t')
            name=line_data[position_name]
            read_type=line_data[position_reads]
            ftp=line_data[position_ftp]
            name_read_tuple=(name,read_type)
            #check to see if organism and seq_type exist
            if name_read_tuple in url_data.keys():
                #check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

#2. Download data
#(already checked if file exists)

def download(url,newdir,newfile):
    filestring=newdir+newfile
    urlstring="wget -O "+newdir+newfile+" "+url
    #Note: only for Python 3
    #urllib.request.urlretrieve(url,filestring)
    #Use this for Python 2
    #subprocess.Popen(urlstring,shell=True,stdout=PIPE)

#3. Extract with fastq-dump (sratools)
    
def sra_extract(newdir,file,seqtype):
    if seqtype=="single":
        sra_string="fastq-dump -v "+newdir+file
        print sra_string
    elif seqtype=="paired":
        sra_string="fastq-dump -v --split-3 "+newdir+file
        print sra_string
    #subprocess.Popen(sra_string,shell=True,stdout=PIPE)
    
#4. Generate fastq from all fastq in directory
#(fastqc module must be loaded by bash script)

def fastqc_report(filelist):
    #imports list of files in each directory
    file_string=" ".join(filelist)
    fastqc_string="fastqc "+file_string
    print fastqc_string
    #subprocess.Popen(fastqc_string,shell=True,stdout=PIPE)

def execute(basedir,url_data):
    for item in url_data.keys():
        #Creates directory for each file to be downloaded
        #Directory will be located according to organism and read type (single or paired)
        organism=item[0]
        seqtype=item[1]
        org_seq_dir=basedir+organism+"/"+seqtype+"/"
        url_list=url_data[item]
        for url in url_list:
            filename=basename(urlparse(url).path)
            newdir=org_seq_dir+filename+"/"
            #Makes a new directory for the new filename
            #Checks to see if it already exists
            if os.path.exists(newdir)==True:
                print "Directory existed: ",newdir
            else:
                os.mkdir(newdir)
                print "Directory made: ",newdir
            log_filename=newdir+filename+".log"
            with open(log_filename,"w") as outputfile:
                fastq_file_list=[]
                #check to see if filename exists in newdir
                if filename in os.listdir(newdir):
                    print "sra exists:",filename
                else:                    
                    download(url,newdir,filename)
                    outputfile.write(url+" downloaded.\n")
                listoffiles=os.listdir(newdir)
		fastqcount=0
		fastq=0
		sra=0
   		for i in listoffiles:
			if i.endswith(".fastq"):
				fastq+=1
				fastq_file_list.append(i)
			elif i.endswith("_fastqc"):
				fastqcount+=1
			elif i.endswith(".sra"):
				sra+=1
		if sra:
			if fastq >=1:
				if fastqcount>=1:
					break
				else:
			                fastqc_report(fastq_file_list)
					outputfile.write("fastqc reports generated for: "+str(fastq_file_list)+"\n")
                	else:
				sra_extract(newdir,filename,seqtype)
                        	outputfile.write(filename+" extracted.\n")
				listofnewfiles=os.listdir(newdir)
				for t in listofnewfiles:
					if i.endswith(".fastq"):
						fastq_file_list.append(t)
				fastqc_report(fastq_file_list)
                                outputfile.write("fastqc reports generated for: "+str(fastq_file_list)+"\n")
            outputfile.close()
            print log_filename,"written."

datafile="MMETSP_SRA_Run_Info_subset.csv
basedir="/home/data/"
url_data=get_data(datafile)
execute(basedir,url_data)

