import os
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
import glob
# custom Lisa module
import clusterfunc

def get_trinity_string(org_seq_dir,file_list,seq_type):
    if seq_type=="paired":
        filename1=file_list[0]
        filename2=file_list[1]
        trinity_string="Trinity.pl --JM 50G --seqType fq --left "+filename1+" --right "+filename2+" --CPU 3"
    elif seq_type=="single":
        filestring=file_list[0]
        trinity_string="Trinity.pl --JM 50G --seqType fq --single "+filestring+" --CPU 3"
    print trinity_string
    return trinity_string

def check_trinity_run(seqdir):
   trinity_dir=seqdir+"trinity/trinity_out_dir/"
   trinity_file=trinity_dir+"Trinity.fasta"
   if os.path.isfile(trinity_file)==False:
        if os.path.isdir(trinity_dir)==False:
            print SRA
            file_list=data_dir[item]
            trinity_string=get_trinity_string(org_seq_dir,file_list,seq_type)
            submit_qsub_trinity(org_seq_dir,organism,seq_type,trinity_string)
        else:
            print "Trinity has already been run before, but unsuccessfully."
            print "The directory will be renamed now."
            trinity_dir_old=org_seq_dir+"trinity/trinity_out_dir_old/"
            print "Old directory name:",trinity_dir_old
            os.rename(trinity_dir,trinity_dir_old)
            print os.path.isdir(trinity_dir_old)
   else:
        print "Trinity has already been run successfully:",trinity_file
        print os.path.isfile(trinity_file)

def execute(basedir,trinitydir,datafile):
	url_data=get_data(datafile)
	#print url_data
	#change directory to trinitydir 
	org_seq_dir=basedir+organism+"/"
	for url in url_list:
		filename=basename(urlparse(url).path)	
		newdir=org_seq_dir+filename+"/"
		for i in listoffiles:
			if i.endswith(".fq")


			
basedir="/mnt/mmetsp/subset/trim_combined/interleave"
trinity_dir="/mnt/mmetsp/trinity"
clusterfunc.check_dir(trinity_dir)
datafile="MMETSP_SRA_Run_Info_subset2.csv"
execute(basedir,datafile)
