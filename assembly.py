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

def execute(basedir,url_data,diginormdir):
	trinity_scripts=[]
	for item in url_data.keys():
        #Creates directory for each file to be downloaded
        #Directory will be located according to organism and read type (single or paired)
        	organism=item[0]
        	seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
		# from here, split paired reads
		# then go do assembly
        	clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
			SRA=basename(urlparse(url).path)
			newdir=org_seq_dir+SRA+"/"
			diginormdir=newdir+"diginorm/"
			diginormfile=diginormdir+SRA+".trimmed.interleaved.keep.abundfilt.fq.gz"
			trinitydir=newdir+"trinity/"
			clusterfunc.check_dir(trinitydir)
			if os.path.isfile(diginormfile):
				print "file exists:",diginormfile
			trinity_script=get_trinity_script(trinitydir,SRA)
			trinity_scripts.append(trinity_script)
			build_files(trinitydir,diginormfile,SRA)
	run_trinity(trinity_scripts)			
	return trinity_script

def build_files(trinitydir,diginormfile,SRA):
# takes diginormfile in,splits reads and put into newdir
	buildfiles=trinitydir+SRA+".buildfiles.sh"
	with open(buildfiles,"w") as buildfile:
   		buildfile.write("python /home/ubuntu/khmer/scripts/split-paired-reads.py -d "+trinitydir+" "+diginormfile+"\n")
		buildfile.write("cat "+trinitydir+"*.1 > "+trinitydir+"left.fq"+"\n")
		buildfile.write("cat "+trinitydir+"*.2 > "+trinitydir+"right.fq"+"\n")
		# need to fix , orphans are now combined for whole dataset, this is incorrect
		# should be separate orphans file for each sample 
		#buildfile.write("gunzip -c orphans.keep.abundfilt.fq.gz >> left.fq")
	s=subprocess.Popen("sudo bash "+str(buildfiles),shell=True)
	s.wait()

def get_trinity_script(trinitydir,SRA):
	trinityfiles=trinitydir+SRA+".trinityfile.sh"	
	s="""#!/bin/bash
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi

${{HOME}}/trinity*/Trinity --left {}left.fq \\
--right {}right.fq --output {}trinity_out --seqType fq --max_memory 14G	\\
--CPU ${{THREADS:-2}}

""".format(trinitydir,trinitydir,trinitydir,trinitydir,trinitydir,trinitydir,trinitydir)
	with open(trinityfiles,"w") as trinityfile:	
		trinityfile.write(s)
#string interpolation
#have .format specify dicionary
	#test_string="cat "+trinityfiles
	#s=subprocess.Popen(test_string,shell=True)
	#s.wait()
	return trinityfiles
#make a new run.sh in ~/MMETSP/ to run all *.trinityfile.sh in serial

def run_trinity(trinity_script_list):
	# need to run serially
	# in general, this is a bad idea
	# under normal circumstances, would run in parallel, one process for each Trinity
	# need to loop through and get name of all Trinity scripts
 	# make a script running all scripts
	print trinity_script_list
	runfile="/home/ubuntu/MMETSP/run.sh"
	with open(runfile,"w") as run_file:
		run_file.write("#!/bin/bash"+"\n") 
		for script in trinity_script_list:
			command="sudo bash "+script
			run_file.write(command+"\n")
	print "File written:",runfile
	print "run with:"
	print "sudo bash run.sh"	

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

basedir="/mnt/mmetsp/"
diginormdir="/mnt/mmetsp/diginorm/"
trinity_dir="/mnt/mmetsp/trinity/"
clusterfunc.check_dir(trinity_dir)
datafile="MMETSP_SRA_Run_Info_subset2.csv"
url_data=get_data(datafile)
execute(basedir,url_data,diginormdir)
