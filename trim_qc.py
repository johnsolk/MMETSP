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
                    print "SRA already exists",sra
                else:
                    sra_name[name].append(sra)
            else:
                sra_name[name]=[sra]
        return sra_list,sra_name

    
# run trimmomatic

def run_trimmomatic_TruSeq3(newdir,file1,file2,sra):
    bash_filename=newdir+sra+".trim.TruSeq3.sh"
    with open(bash_filename,"w") as bash_file:
        bash_file.write("#!/bin/bash\n")
	bash_file.write("java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\"+"\n")
        bash_file.write("-threads 8 -baseout "+sra+".Phred30.TruSeq3.fq \\"+"\n")
        bash_file.write(file1+" \\"+"\n")
        bash_file.write(file2+" \\"+"\n")
        bash_file.write("ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq3-PE.fa:2:30:10 \\"+"\n")
        bash_file.write("SLIDINGWINDOW:4:30 \\"+"\n")
        bash_file.write("LEADING:30 \\"+"\n")
        bash_file.write("TRAILING:30 \\"+"\n")
        bash_file.write("MINLEN:25")
    bash_file.close()
    print "file written:",bash_filename

def run_trimmomatic_TruSeq2(newdir,file1,file2,sra):
    bash_filename=newdir+sra+".trim.TruSeq2.sh"
    with open(bash_filename,"w") as bash_file:
	bash_file.write("#!/bin/bash\n")
        bash_file.write("java -Xmx10g -jar /home/ubuntu/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\"+"\n")
        bash_file.write("-threads 8 -baseout "+sra+".Phred30.TruSeq2.fq \\"+"\n")
        bash_file.write(file1+" \\"+"\n")
        bash_file.write(file2+" \\"+"\n")
        bash_file.write("ILLUMINACLIP:/home/ubuntu/bin/Trimmomatic-0.33/adapters/TruSeq2-PE.fa:2:30:10 \\"+"\n")
        bash_file.write("SLIDINGWINDOW:4:30 \\"+"\n")
        bash_file.write("LEADING:30 \\"+"\n")
        bash_file.write("TRAILING:30 \\"+"\n")
        bash_file.write("MINLEN:25")
    bash_file.close()
    print "file written:",bash_filename

def interleave_reads(trimdir,sra):
    interleave_string_TS2="python /usr/local/share/khmer/scripts/interleave-reads.py "+trimdir+sra+".Phred30.TruSeq2_1P.fq "+trimdir+sra+".Phred30.TruSeq2_2P.fq > "+trimdir+sra+".TS2.interleaved.fq"
    interleave_string_TS3="python /usr/local/share/khmer/scripts/interleave-reads.py "+trimdir+sra+".Phred30.TruSeq3_1P.fq "+trimdir+sra+".Phred30.TruSeq3_2P.fq > "+trimdir+sra+".TS3.interleaved.fq"
    #print interleave_string_TS2
    #print interleave_string_TS3
    #s1=subprocess.Popen(interleave_string_TS2,shell=True)    
    #s1.wait()
    #s2=subprocess.Popen(interleave_string_TS3,shell=True)
    #s2.wait()

def run_jellyfish(trimdir,sra):
    jellyfish_string1_TS2="jellyfish count -m 25 -s 200M -t 8 -C -o "+trimdir+sra+".TS2.jf "+trimdir+sra+".TS2.interleaved.fq"
    jellyfish_string2_TS2="jellyfish histo "+trimdir+sra+".TS2.jf -o "+trimdir+sra+".TS2.histo"	
    jellyfish_string1_TS3="jellyfish count -m 25 -s 200M -t 8 -C -o "+trimdir+sra+".TS3.jf "+trimdir+sra+".TS3.interleaved.fq"
    jellyfish_string2_TS3="jellyfish histo "+trimdir+sra+".TS3.jf -o "+trimdir+sra+".TS3.histo"
    s1=subprocess.Popen(jellyfish_string1_TS2,shell=True)
    s1.wait()
    s2=subprocess.Popen(jellyfish_string2_TS2,shell=True)
    s2.wait()
    s3=subprocess.Popen(jellyfish_string1_TS3,shell=True)
    s3.wait()
    s4=subprocess.Popen(jellyfish_string2_TS3,shell=True)
    s4.wait()
    

def execute(datadir,trimdir,sra_list):
    for sra in sra_list:
	file1=datadir+sra+"_1.subset40k.fastq"
	file2=datadir+sra+"_2.subset40k.fastq"	
	if os.path.isfile(file1) and os.path.isfile(file2):
		#run_trimmomatic_TruSeq2(trimdir,file1,file2,sra)
		#run_trimmomatic_TruSeq3(trimdir,file1,file2,sra)
		#interleave_reads(trimdir,sra)
                run_jellyfish(trimdir,sra)
	else:
		print "Files do not exist:",file1,file2 	
	


datafile="MMETSP_SRA_Run_Info_subset.csv"
trimdir="/home/ubuntu/data/trim/"
datadir="/home/ubuntu/data/"
basedir="/home/ubuntu/"
sra_list,sra_name=get_sra(datafile)
print sra_list
execute(datadir,trimdir,sra_list)




