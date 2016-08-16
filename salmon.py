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

def salmon_index(salmondir,sra,trinity_fasta):
	index=sra+"_index"
	salmon_index_string="salmon index --index "+index+" --transcripts "+trinity_fasta+" --type quasi"
	return index,salmon_index_string

def quant_salmon(salmondir,sra,newdir,trinity_fasta):
	file1=newdir+"trim/"+sra+".trim_1P.fq"
	file2=newdir+"trim/"+sra+".trim_2P.fq"
	if os.path.isfile(file1):
		print "file exists:",file1
	if os.path.isfile(file2):
		print "file exists:",file2
	index,salmon_index_string = salmon_index(salmondir,sra,trinity_fasta)
	salmon_string="salmon quant -i "+index+" --libType IU -1 "+file1+" -2 "+file2+" -o "+salmondir+sra+".quant --dumpEq --auxDir aux"
	commands = [salmon_index_string,salmon_string]
	process_name = "salmon"
	module_name_list = ""
	filename = sra
	#s=subprocess.Popen(salmon_index_string,shell=True)
	#s.wait()
	clusterfunc.qsub_file(salmondir,process_name,module_name_list,filename,commands)	
	
def gather_counts():
        gather_counts_string="python /home/ubuntu/MMETSP/gather-counts.py"
	return gather_counts_string
	
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
			trinity_fasta=trinitydir+"Trinity.fasta"
			quant_salmon(salmondir,sra,newdir,trinity_fasta)

basedir="/mnt/scratch/ljcohen/mmetsp/"
datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
	"MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]
for datafile in datafiles:
	url_data=get_data(datafile)
	print url_data
	execute(url_data)
