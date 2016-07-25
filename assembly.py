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

def execute(basedir,url_data):
	count = 1
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
			diginormfile=diginormdir+"qsub_files/"+SRA+".trimmed.interleaved.fq.keep.abundfilt.pe"
			trinitydir=newdir+"trinity/"
			clusterfunc.check_dir(trinitydir)
			if os.path.isfile(diginormfile):
				#print "file exists:",diginormfile
				#rename_files(trinitydir,diginormdir,diginormfile,SRA)
			        run_trinity(trinitydir,SRA)	
			else:
				"Re-run diginorm:",diginormfile
			#count = check_trinity(newdir,SRA,count)
	#print "Number of times Trinity needs to be re-run:",count

def combine_orphans(diginormdir):
	diginorm_files_dir = diginormdir + "qsub_files/"
	rename_orphans="""
gzip -9c {}orphans.fq.gz.keep.abundfilt > {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
        gzip -9c ${{file}} >> {}orphans.keep.abundfilt.fq.gz
done
""".format(diginorm_files_dir,diginormdir,diginorm_files_dir,diginormdir)
	return rename_orphans

def rename_files(trinitydir,diginormdir,diginormfile,SRA):
# takes diginormfile in,splits reads and put into newdir
	rename_orphans = combine_orphans(diginormdir)
	split_paired = "split-paired-reads.py -d "+diginormdir+" "+diginormfile
	rename_string1 = "cat "+diginormdir+"*.1 > "+trinitydir+SRA+".left.fq"
	rename_string2 = "cat "+diginormdir+"*.2 > "+trinitydir+SRA+".right.fq"
	rename_string3 = "gunzip -c "+diginormdir+"orphans.keep.abundfilt.fq.gz >> "+trinitydir+SRA+".left.fq"
	commands=[rename_orphans,split_paired,rename_string1,rename_string2,rename_string3]
        process_name="rename"
        module_name_list=["GNU/4.8.3","khmer/2.0"]
        filename=SRA
        clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)

def run_trinity(trinitydir,SRA):
	trinity_command="""
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
#if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi

Trinity --left {}{}.left.fq \\
--right {}{}.right.fq --output {}trinity_out --seqType fq --JM 20G --CPU 16

""".format(trinitydir,trinitydir,trinitydir,trinitydir,trinitydir,SRA,trinitydir,SRA,trinitydir)
	commands=[trinity_command]
        process_name="trinity"
        module_name_list=["trinity/20140413p1"]
        filename=SRA
        clusterfunc.qsub_file(trinitydir,process_name,module_name_list,filename,commands)

def check_trinity(seqdir,SRA,count):
   trinity_dir=seqdir+"trinity/"
   trinity_file=trinity_dir+"trinity_out/Trinity.fasta"
   if os.path.isfile(trinity_file)==False:
        if os.path.isdir(trinity_dir)==False:
            print "Still need to run.",trinity_dir
            run_trinity(trinity_dir,SRA)
            count += 1
	else:
            print "Incomplete:",trinity_dir
	    run_trinity(trinity_dir,SRA)
	    count += 1 
   return count
basedir="/mnt/scratch/ljcohen/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset_msu3.csv"
url_data=get_data(datafile)
execute(basedir,url_data)
