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
	print "File removed:",filename

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
			
			##
			# run this after trim_qc.py
			##

			#if os.path.isfile(filename+"_1.fastq"):
			#	delete_file(filename+"_1.fastq")
			#if os.path.isfile(filename+"_2.fastq"):
			#	delete_file(filename+"_2.fastq")	
			
			##
			# run this after getdata.py
			##
	    		#if os.path.isfile(filename):
			#	print "File exists:",filename 	
			#	delete_file(filename)
		

			##
			# run this after all diginorm steps have finished
			##
	
			#diginormdir=newdir+"diginorm/"
			#os.chdir(diginormdir)
			#diginorm_delete_files=["norm.C20k20.ct","orphans.fq.gz.keep.abundfilt"]
			#for filename in glob.glob("*.keep"):
		#		diginorm_delete_files.append(filename)
		#	for filename in glob.glob("*.abundfilt"):
		#		diginorm_delete_files.append(filename)
		#	for filename in glob.glob("*.abundfilt.pe"):
		#		diginorm_delete_files.append(filename)
		#	for filename in glob.glob("*.abundfilt.se"):
		#		diginorm_delete_files.append(filename)
		#	print diginorm_delete_files
		#	for filetodelete in diginorm_delete_files:
		#		if os.path.isfile(filetodelete):
		#			print "File in diginorm to delete exists:",filetodelete
		#			delete_file(filetodelete)
		#		else:
		#			print "File in diginorm not found:",filetodelete
		#	os.chdir("/home/ubuntu/MMETSP/")

			##
			# run this after assembly.py
			# to delete extra files
			##
				
			trinitydir=newdir+"trinity/"
			os.chdir(trinitydir)
			listoffiles=os.listdir(trinitydir)
			filestodelete=[]
			for filename in listoffiles:
				if filename.endswith(".fq.gz.1"):
					filestodelete.append(filename)
				if filename.endswith(".fq.gz.2"):
					filestodelete.append(filename)
			print "These files will be deleted:",filestodelete
			for i in filestodelete:
				delete_file(i)


basedir="/mnt/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset_b.csv"
url_data=get_data(datafile)
print url_data
execute(url_data)
