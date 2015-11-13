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
    for item in url_data.keys():
        #Creates directory for each file to be downloaded
        #Directory will be located according to organism and read type (single or paired)
        organism=item[0]
        seqtype=item[1]
        org_seq_dir=basedir+organism+"/"
        print org_seq_dir
	# from here, split paired reads
	# then go do assembly
        clusterfunc.check_dir(org_seq_dir)
        url_list=url_data[item]
        for url in url_list:
		SRA=basename(urlparse(url).path)
		print SRA
		newdir=org_seq_dir+SRA+"/"
		print newdir
		get_files(diginormdir,SRA,newdir)
		
		
def get_files(diginormdir,SRA,newdir):
	listoffiles=os.listdir(diginormdir)
	for i in listoffiles:
		if i.startswith(SRA):
			# make symbolic link to i in newdir
			sym_link="ln -fs "+diginormdir+i+" "+newdir
			print sym_link
			s=subprocess.Popen(sym_link,shell=True)
			s.wait()
			sym_link_file=newdir+i
			#build_files(newdir,SRA,sym_link_file)				
# takes file in /mnt/mmetsp/diginorm/ , startswith SRA filename
# splits reads and put into newdir
			run_trinity(newdir,SRA)			

def build_files(newdir,SRA,sym_link_file):
	buildfiles=newdir+SRA+".buildfiles.sh"
	print sym_link_file
	print buildfiles
	with open(buildfiles,"w") as buildfile:
   		buildfile.write("python /home/ubuntu/khmer/scripts/split-paired-reads.py -d "+newdir+" "+str(sym_link_file)+"\n")
		buildfile.write("cat "+newdir+"*.1 > "+newdir+"left.fq"+"\n")
		buildfile.write("cat "+newdir+"*.2 > "+newdir+"right.fq"+"\n")
		# orphans are messed up with the way the current files are
		#buildfile.write("gunzip -c orphans.keep.abundfilt.fq.gz >> left.fq")
	s=subprocess.Popen("bash "+str(buildfiles),shell=True)
	s.wait()

def run_trinity(newdir,SRA):
	trinityfiles=newdir+SRA+".trinityfile.sh"
	with open(trinityfiles,"w") as trinityfile:
		trinityfile.write("${HOME}/trinity*/Trinity --left "+newdir+"left.fq \\"+"\n")
  		trinityfile.write("--right "+newdir+"right.fq --output "+newdir+" --seqType fq --max_memory 14G \\"+"\n")
  		trinityfile.write("--CPU ${THREADS:-2}"+"\n")
	s=subprocess.Popen("cat "+str(trinityfiles),shell=True)
	s.wait()

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
print url_data
execute(basedir,url_data,diginormdir)
