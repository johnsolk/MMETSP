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
import string
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
<<<<<<< .merge_file_ylVy1d
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
	file1=newdir+"trim/"+sra+".Phred30.TruSeq_1P.fq"
	file2=newdir+"trim/"+sra+".Phred30.TruSeq_2P.fq"
=======
	salmon_index_string="salmon index --index "+index+" --transcripts "+trinity_fasta+" --type quasi"
	return index,salmon_index_string

def quant_salmon(salmondir,sra,newdir,trinity_fasta):
	file1=newdir+"trim/"+sra+".trim_1P.fq"
	file2=newdir+"trim/"+sra+".trim_2P.fq"
>>>>>>> .merge_file_hxAl3W
	if os.path.isfile(file1):
		print "file exists:",file1
	else:
		print "missing:",file1
	if os.path.isfile(file2):
		print "file exists:",file2
<<<<<<< .merge_file_ylVy1d
	else:
		print "missing:",file2
	salmon_string="salmon quant -i "+index+" --libType IU -1 "+file1+" -2 "+file2+" -o "+salmondir+sra+".quant"
        s=subprocess.Popen(salmon_string,shell=True)
	s.wait()
	os.chdir("/home/ubuntu/MMETSP/")
=======
	index,salmon_index_string = salmon_index(salmondir,sra,trinity_fasta)
	salmon_string="salmon quant -i "+index+" --libType IU -1 "+file1+" -2 "+file2+" -o "+salmondir+sra+".quant --dumpEq --auxDir aux"
	commands = [salmon_index_string,salmon_string]
	process_name = "salmon"
	module_name_list = ""
	filename = sra
	clusterfunc.qsub_file(salmondir,process_name,module_name_list,filename,commands)	
	
def gather_counts():
        gather_counts_string="python /home/ubuntu/MMETSP/gather-counts.py"
	return gather_counts_string
>>>>>>> .merge_file_hxAl3W
	


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
	link_command="cp "+salmondir+sra+".quant.counts "+counts_files_dir+sra+".counts" 
	print link_command
	s=subprocess.Popen(link_command,shell=True)
        s.wait()

def fix_salmon_counts(salmondir,sra):
	counts_files_dir="/home/ubuntu/MMETSP/counts/"
	counts_file=salmondir+sra+".quant.counts"
	new_counts_file=salmondir+sra+".counts"
#open file
#go line by line
#if line starts with TR
#replace all '|' with '-'
#and add sra  + "_" to the beginning of each line
	with open(counts_file) as thefile:
		#with open (new_counts_file) as thenewfile:
			for line in thefile:
				if line.startswith("TR"):
					print line
					replaced = line.replace('\|','-')
					print replaced				
					#thenewfile.write(replaced+"\n")	


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
<<<<<<< .merge_file_ylVy1d
			trinity_fasta=trinitydir+sra+".Trinity.fixed.fa"
			#index=salmon_index(salmondir,sra,trinity_fasta)
			#quant_salmon(salmondir,index,sra,newdir)
			#gather_counts(salmondir)		
			#sim_link(salmondir,sra)			
			fix_salmon_counts(salmondir,sra)

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
=======
			trinity_fasta=trinitydir+"Trinity.fasta"
			quant_salmon(salmondir,sra,newdir,trinity_fasta)

basedir="/mnt/scratch/ljcohen/mmetsp/"
datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
	"MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]
for datafile in datafiles:
	url_data=get_data(datafile)
	print url_data
	execute(url_data)
>>>>>>> .merge_file_hxAl3W
