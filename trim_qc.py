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
    sra_name_dictionary={}
    sra_list=[]
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
	#print headerline        
        position_run=headerline.index("Run")
        position_name=headerline.index("ScientificName")
        for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            sra=line_data[position_reads]
            sra_list.append(sra)
            if name in sra_name.keys():
                if sra in sra_name[name]:
                    print "SRA already exists",sra
                else:
                    sra_name[name].append(sra)
            else:
                sra_name[name]=[sra]
        return sra_list,sra_name

    
# run trimmomatic

def run_trimmomatic_TruSeq3(newdir,sra,filelist):
    bash_filename=newdir+sra+"trim.bash"
    with open(bash_filename,"w") as bash_file:
        bash_file.write("java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\"+"\n")
        bash_file.write("-threads 8 -baseout "+sra+".Phred30.TruSeq3.fq \\"+"\n")
        bash_file.write("/mnt/reads/root_S13.R1.fq \\"+"\n")
        bash_file.write("/mnt/reads/root_S13.R2.fq \\"+"\n")
        bash_file.write("ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq3-PE.fa:2:30:10 \\"+"\n")
        bash_file.write("SLIDINGWINDOW:4:30 \\"+"\n")
        bash_file.write("LEADING:30 \\"+"\n")
        bash_file.write("TRAILING:30 \\"+"\n")
        bash_file.write("MINLEN:25")
    bash_file.close()

def run_trimmomatic_TruSeq2(newdir,sra,filelist):
    bash_filename=newdir+sra+"trim.bash"
    with open(bash_filename,"w") as bash_file:
        bash_file.write("java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\"+"\n")
        bash_file.write("-threads 8 -baseout "+sra+".Phred30.TruSeq2.fq \\"+"\n")
        bash_file.write("/mnt/reads/root_S13.R1.fq \\"+"\n")
        bash_file.write("/mnt/reads/root_S13.R2.fq \\"+"\n")
        bash_file.write("ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq2-PE.fa:2:30:10 \\"+"\n")
        bash_file.write("SLIDINGWINDOW:4:30 \\"+"\n")
        bash_file.write("LEADING:30 \\"+"\n")
        bash_file.write("TRAILING:30 \\"+"\n")
        bash_file.write("MINLEN:25")
    bash_file.close()


datafile="MMETSP_SRA_Run_Info_subset.csv"
basedir="/home/ubuntu/"
sra_list,sra_name=get_sra(datafile)
print sra_list



