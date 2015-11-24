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

def get_sra(thefile):
    sra_name={}
    sra_list=[]
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
	#print headerline        
        position_run=headerline.index("Run")
        position_name=headerline.index("ScientificName")
        for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            sra=line_data[position_run]
            sra_list.append(sra)
            if name in sra_name.keys():
                if sra in sra_name[name]:
                    print "SRA exists",sra
                else:
                    sra_name[name].append(sra)
            else:
                sra_name[name]=[sra]
        return sra_list,sra_name
    
# run trimmomatic

def run_trimmomatic_TruSeq(trimdir,file1,file2,sra):
    bash_filename=trimdir+sra+".trim.TruSeq.sh"
    if os.path.isfile(bash_filename):
	print "trim file already written",bash_filename
    else:	
	with open(bash_filename,"w") as bash_file:
        	bash_file.write("#!/bin/bash\n")
		bash_file.write("java -Xmx10g -jar /bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\"+"\n")
        	bash_file.write("-threads 8 -baseout "+sra+".Phred30.TruSeq.fq \\"+"\n")
        	bash_file.write(file1+" \\"+"\n")
        	bash_file.write(file2+" \\"+"\n")
        	bash_file.write("ILLUMINACLIP:/bin/Trimmomatic-0.33/adapters/combined.fa:2:30:10 \\"+"\n")
        	bash_file.write("SLIDINGWINDOW:4:30 \\"+"\n")
        	bash_file.write("LEADING:30 \\"+"\n")
        	bash_file.write("TRAILING:30 \\"+"\n")
		bash_file.write("MINLEN:25 &> trim."+sra+".log"+"\n")
    	print "file written:",bash_filename

def make_orphans(trimdir):
    if os.path.isfile(trimdir+"orphans.fq.gz"):
	print "orphans file exists:",trimdir+"orphans.fq.gz"
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

def interleave_reads(trimdir,sra):
    interleavedir="/mnt/mmetsp/subset/trim/interleave/"
    interleavefile=interleavedir+sra+".trimmed.interleaved.fq"
    if os.path.isfile(interleavefile):
	print "already interleaved"
    else:
    	interleave_string="python /usr/local/share/khmer/scripts/interleave-reads.py "+trimdir+sra+".Phred30.TruSeq_1P.fq "+trimdir+sra+".Phred30.TruSeq_2P.fq > "+interleavefile
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

def execute(datadir,trimdir,fastqcdir,sra_list):
    for sra in sra_list:
	file1=datadir+sra+"_1.subset100k.fastq"
	file2=datadir+sra+"_2.subset100k.fastq"	
	if os.path.isfile(file1) and os.path.isfile(file2):
		print file1
		print file2
		#fastqc_report(datadir,fastqcdir)
		### need to fix so the following steps run themselves:
		#run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
		#print "run Trimmomatic on all bash files with this:"
		#print "cd "+trimdir
		#print "parallel -j0 bash :::: <(ls *.sh)"
		####
		interleave_reads(trimdir,sra)
                #run_jellyfish(trimdir,sra)
	else:
		print "Files do not exist:",file1,file2 	
    make_orphans(trimdir)
    #run fastqc on all files
    #fastqc_report(trimdir,fastqcdir)	


datafile="/home/ubuntu/MMETSP/MMETSP_SRA_Run_Info_subset2.csv"
trimdir="/mnt/mmetsp/subset/trim/"
clusterfunc.check_dir(trimdir)
interleave=trimdir+"interleave/"
clusterfunc.check_dir(interleave)
basedir="/mnt/mmetsp/subset/"
datadir=basedir
fastqcdir="/mnt/mmetsp/subset/trim_combined/fastqc/"
sra_list,sra_name=get_sra(datafile)
print sra_list
execute(datadir,trimdir,fastqcdir,sra_list)
#fastqc_report(fastqcdir)



