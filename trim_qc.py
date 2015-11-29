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
    # need a better check for whether this process has been run:
    #if os.path.isfile(bash_filename):
#	print "trim file already written",bash_filename
 #   else:
	j="""#!/bin/bash
java -Xmx10g -jar /bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.Phred30.TruSeq.fq \\
{} {} \\
ILLUMINACLIP:/bin/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
	os.chdir(trimdir)	
	with open(bash_filename,"w") as bash_file:
		bash_fil.write(j)
    	print "file written:",bash_filename
    	print "Trimming with Trimmomatic now..."
	s=subprocess.Popen("sudo bash "+bash_filename,shell=True)
    	s.wait()
    	print "Trimmomatic completed."
    	os.chdir("/home/ubuntu/MMETSP/")

def make_orphans(trimdir):
    #if os.path.isfile(trimdir+"orphans.fq.gz"):
#	print "orphans file exists:",trimdir+"orphans.fq.gz"
 #   else:
	listoffiles=os.listdir(trimdir)
    	orphanreads=[]
    	for i in listoffiles:
		if i.endswith("_1U.fq"):
			orphanreads.append(trimdir+i)
		elif i.endswith("_2U.fq"):
			orphanreads.append(trimdir+i)
    	# does it matter what order the orphans are added?
	# it seems that 2P is always empty, is that normal?
	orphanlist=" ".join(orphanreads)
    	print orphanlist
    	orphan_string="gzip -9c "+orphanlist+" > "+trimdir+"orphans.fq.gz"
    	print orphan_string
    	s=subprocess.Popen(orphan_string,shell=True)
    	s.wait()

def fastqc_report(trimdir,fastqcdir):
    # imports list of files in each directory
    listoffiles=os.listdir(trimdir)
    #print listoffiles
    fastq_file_list=[]
    #for filename in listoffiles:
#	if filename.endswith(".TruSeq_1U.fq"):
#		fastq_file_list.append(fastqcdir+filename)
#	elif filename.endswith(".TruSeq_2U.fq"):
#		fastq_file_list.append(fastqcdir+filename)
    for o  in listoffiles:
	if o.endswith(".fq"):
		fastq_file_list.append(trimdir+o)
    #print fastq_file_list
    # creates command to generate fastqc reports from all files in list 
    file_string=str(fastq_file_list)
    #print fastq_file_list
    file_string=" ".join(fastq_file_list)
    #print file_string
    fastqc_string="fastqc -o "+fastqcdir+" "+file_string
    print fastqc_string
    #print "fastqc reports generated for: "+str(fastq_file_list)
    s=subprocess.Popen(fastqc_string,shell=True)
    s.wait()

def interleave_reads(trimdir,sra,interleavedir):
    	interleavefile=interleavedir+sra+".trimmed.interleaved.fq"
    #if os.path.isfile(interleavefile):
#	print "already interleaved"
 #   else:
    	interleave_string="interleave-reads.py "+trimdir+sra+".Phred30.TruSeq_1P.fq "+trimdir+sra+".Phred30.TruSeq_2P.fq > "+interleavefile
    	print interleave_string
	print "Interleaving now..."
    	s=subprocess.Popen(interleave_string,shell=True)    
    	s.wait()
	print "Reads interleaved."

def run_jellyfish(trimdir,sra):
    jellyfish_string1_TS2="jellyfish count -m 25 -s 200M -t 8 -C -o "+trimdir+sra+".TS2.jf "+trimdir+sra+".TS2.interleaved.fq"
    jellyfish_string2_TS2="jellyfish histo "+trimdir+sra+".TS2.jf -o "+trimdir+sra+".TS2.histo"	
    jellyfish_string1_TS3="jellyfish count -m 25 -s 200M -t 8 -C -o "+trimdir+sra+".TS3.jf "+trimdir+sra+".TS3.interleaved.fq"
    jellyfish_string2_TS3="jellyfish histo "+trimdir+sra+".TS3.jf -o "+trimdir+sra+".TS3.histo"
    #s1=subprocess.Popen(jellyfish_string1_TS2,shell=True)
    #s1.wait()
    #s2=subprocess.Popen(jellyfish_string2_TS2,shell=True)
    #s2.wait()
    #s3=subprocess.Popen(jellyfish_string1_TS3,shell=True)
    #s3.wait()
    #s4=subprocess.Popen(jellyfish_string2_TS3,shell=True)
    #s4.wait() 

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
		if os.path.isfile(file1) and os.path.isfile(file2):
			print file1
			print file2
			#fastqc_report(datadir,fastqcdir)
			### need to fix so the following steps run themselves:
			#run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
			interleave_reads(trimdir,sra,interleavedir)
                	#run_jellyfish(trimdir,sra)
			make_orphans(trimdir)
		else:
			print "Files do not exist:",file1,file2 	
    #run fastqc on all files
    #fastqc_report(trimdir,fastqcdir)	


datafile="/home/ubuntu/MMETSP/MMETSP_SRA_Run_Info_subset2.csv"
datadir="/mnt/mmetsp/"
url_data=get_data(datafile)
print url_data
execute(url_data,datadir)
#fastqc_report(fastqcdir)



