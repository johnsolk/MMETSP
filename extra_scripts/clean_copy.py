import os
import os.path
from os.path import basename
from urllib import urlopen
from urlparse import urlparse
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
from shutil import copyfile
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

def send_to_cluster(basedir,commands,name):
    	process_name = "delete"
    	module_name_list = ""
    	filename = name
    	clusterfunc.qsub_file(basedir, process_name, module_name_list, filename, commands)


def copy_file(srcfile,dstdir):
	shutil.copy(srcfile, dstdir)
	print "Copied:",dstdir

def copy_dir(srcdir,dstdir):
	shutil.copytree(srcdir,dstdir)
	print "Copied:",dstdir

def execute(basedir, newdir, url_data):
    for item in url_data:
        organism = item[0].replace("'","")
        org_seq_dir = basedir + organism + "/"
        mmetsp = item[2]
        if mmetsp.endswith("_2"):
		mmetsp = mmetsp.split("_")[0]
	sra = item[1]
        newdir_sra = org_seq_dir + sra + "/"
	sra_transrate_1 = newdir_sra + "transrate_dib_v_ncgr_cds/"
	sra_transrate_2 = newdir_sra + "transrate_ncgr_cds_v_dib/"
	sra_transrate = newdir_sra + "transrate/"
	sra_trim = newdir_sra + "trim/"
	sra_trim_1P = sra_trim + sra + ".trim_1P.fq"
	sra_trim_2P = sra_trim + sra + ".trim_2P.fq"
	sra_busco = newdir_sra + "busco/"
		


	newdir_mmetsp = newdir + mmetsp + "/"
	newdir_mmetsp_sra = newdir_mmetsp + "sra/"
	newdir_mmetsp_sra_transrate = newdir_mmetsp_sra + "transrate/"
	newdir_mmetsp_sra_trim = newdir_mmetsp_sra + "trim/"
	newdir_mmetsp_sra_busco = newdir_mmetsp_sra + "busco/"
	newdir_mmetsp_sra_fastqc = newdir_mmetsp_sra + "fastqc_raw/"
	clusterfunc.check_dir(newdir_mmetsp_sra)
	clusterfunc.check_dir(newdir_mmetsp_sra_transrate)
	clusterfunc.check_dir(newdir_mmetsp_sra_trim)
	clusterfunc.check_dir(newdir_mmetsp_sra_busco)
	clusterfunc.check_dir(newdir_mmetsp_sra_fastqc)
	
	if os.path.isdir(newdir_sra):
		print "Exists:",newdir_sra
	else:
		print "Missing:",newdir_sra
	if os.path.isdir(newdir_mmetsp):
		print "Exists:",newdir_mmetsp
	else:
		print "Missing:",newdir_mmetsp		
	
	# copy_transrate1 =  
	
	#copy_transrate2 = 
	
	#copy_transrate_scores = 
	
	#copy_trim_reads = 
	ged_trim = "/mnt/research/ged/data/mmetsp/trimmed_reads/"
	copy_file(sra_trim_1P,ged_trim)
	copy_file(sra_trim_2P,ged_trim)
	#copy_busco = 
	#copy_fastqc = 
		

basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
newdir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "../SraRunInfo_719.csv"
url_data = get_data(datafile)
print url_data
execute(basedir,newdir,url_data)
