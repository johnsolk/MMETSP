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
    count = 0
    url_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_ftp = headerline.index("download_path")
        position_mmetsp = headerline.index("SampleName")
	for line in inputfile:
            	line_data = line.split(',')
            	name = "_".join(line_data[position_name].split())
            	read_type = line_data[position_reads]
            	mmetsp = line_data[position_mmetsp]
		ftp = line_data[position_ftp]
            	name_read_tuple = (name, read_type, mmetsp)
            	print name_read_tuple
            	# check to see if Scientific Name and run exist
            	if name_read_tuple in url_data.keys():
                	if ftp in url_data[name_read_tuple]:
                    		print "url already exists:", ftp
                	else:
            	        	url_data[name_read_tuple].append(ftp)
            	else:
                	url_data[name_read_tuple] = [ftp]
        return url_data

def check_empty(empty_files, file, sra):
    if os.stat(file).st_size == 0:
        print "File is empty:", file
        if sra not in empty_files:
            empty_files.append(sra)
    return empty_files

def check_trinity(assemblies,trinity_fail, trinity_file, sra):
    if os.path.isfile(trinity_file):
        print "Trinity completed successfully:", trinity_file
	assemblies.append(sra)
    else:
        print "Trinity needs to be run again:", trinity_file
        trinity_fail.append(sra)
    return trinity_fail,assemblies

def send_to_cluster(basedir,commands,name):
    process_name = "copy"
    module_name_list = ""
    filename = name
    #clusterfunc.qsub_file(basedir, process_name, module_name_list, filename, commands)

def copy_fastq_filesdir(newdir,file1):
        cp_string = "cp "+file1+" "+newdir
        return cp_string

def move_files(url_data,basedir,newdir):
	for item in url_data:
                organism = item[0].replace("'","")
                sra = item[1]
                mmetsp = item[2]
		if mmetsp.endswith("_2"):
			mmetsp = mmetsp.split("_")[0]
		org_seq_dir = basedir + organism + "/" + sra + "/"
		mmetsp_dir = newdir + mmetsp + "/"
	        print mmetsp_dir
		clusterfunc.check_dir(mmetsp_dir)
		file1_old = org_seq_dir + "trinity/" + sra + ".left.fq"
		file2_old = org_seq_dir + "trinity/" + sra + ".right.fq"
		file1_new = mmetsp_dir + sra + ".left.fq"
		file2_new = mmetsp_dir + sra + ".right.fq"
		if os.path.isfile(file1_new):
			if os.path.isfile(file2_new):
				print file1_new
				print file2_new
		else:			
			cp_string1 = copy_fastq_filesdir(mmetsp_dir,file1_old)
			cp_string2 = copy_fastq_filesdir(mmetsp_dir,file2_old)
			commands = [cp_string1,cp_string2]
			id = sra + "_" + mmetsp
			send_to_cluster(basedir,commands,id)
			print cp_string1
			print cp_string2

def run_trinity(trinitydir, left, right, SRA):
    trinity_command = """
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
#if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi
Trinity --left {} \\
--right {} --output {}trinity_out --seqType fq --JM 20G --CPU 16
""".format(trinitydir, trinitydir, trinitydir, trinitydir, left, right, trinitydir)
    commands = [trinity_command]
    process_name = "trinity"
    module_name_list = ["trinity/20140413p1"]
    filename = SRA
    clusterfunc.qsub_file(trinitydir, process_name,
                          module_name_list, filename, commands)

def get_trinity(url_data,newdir,basedir):
	count = []
	missing = []
	for item in url_data:
		organism = item[0].replace("'","")
		sra = item[1]
		mmetsp = item[2]
		if mmetsp.endswith("_2"):
			mmetsp = mmetsp.split("_")[0]
		mmetsp_dir = newdir + mmetsp + "/"
		org_seq_dir = basedir + organism + "/" + sra + "/"
		file1 = mmetsp_dir + sra + ".left.fq"
		file2 = mmetsp_dir + sra + ".right.fq"
		trinity_fasta = org_seq_dir + "trinity/" + sra + ".Trinity.fasta" 
		trinity_fasta = org_seq_dir + "trinity/" + organism + "_" + sra + ".Trinity.fixed.fasta"
		#if os.path.isfile(file1) and os.path.isfile(file2):
	#		print file1
	#		print file2
	#		run_trinity(mmetsp_dir,file1,file2,mmetsp)
	#	else:
	#		print "missing:",file1
		if os.path.isfile(trinity_fasta):
			print trinity_fasta
			count.append(trinity_fasta)
			cp_string = "cp " + trinity_fasta + " " + mmetsp_dir
			print cp_string
			s = subprocess.Popen(cp_string, shell = True)
                        s.wait()
		else:
			print "Missing:",trinity_fasta 
			missing.append(trinity_fasta)
	print len(count)
	print missing

basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
newdir = "/mnt/scratch/ljcohen/mmetsp/"
clusterfunc.check_dir(newdir)
datafile = "../SraRunInfo_719.csv"
url_data = get_data(datafile)
print url_data
print len(url_data)
#move_files(url_data,basedir,newdir)
get_trinity(url_data,newdir,basedir)
