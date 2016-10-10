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
import pandas as pd
# custom Lisa module
import clusterfunc


def copy_files(count,ncgr_dir,mmetsp_dir,mmetsp,mmetsp_assemblies):
	trinity_fasta = mmetsp_dir + mmetsp + ".Trinity.fixed.fasta"
	if os.path.isfile(trinity_fasta):
		#print trinity_fasta
		# copy fasta_file, which is combined assemblies, from mmetsp dir to mmetsp_assemblies
		cp_string = "cp " + trinity_fasta + " " + mmetsp_dir + mmetsp + ".Trinity.fasta"
		print cp_string
		s = subprocess.Popen(cp_string, shell=True)
                s.wait()
		# find old individual SRR assemblies and delete them, since this will be replacement
		old_files = os.listdir(mmetsp_assemblies)
		print mmetsp
		alt_mmetsp = mmetsp + "_2"
		old_assemblies1 = sorted([s for s in old_files if mmetsp in s.split("_") or alt_mmetsp in s.split("_")])
		old_assemblies2 = sorted([s for s in old_files if s.split(".")[0].endswith(mmetsp) or s.split(".")[0].endswith(alt_mmetsp)])
		old_assemblies = old_assemblies1 + list(set(old_assemblies2) - set(old_assemblies1))
		for old_assembly in old_assemblies:
			full_assembly = mmetsp_assemblies + old_assembly
			if os.path.isfile(full_assembly):
				print full_assembly
				count +=1
				os.remove(full_assembly)
			else:
				print "Removed:",old_assembly	
			#os.remove(mmetsp_assemblies+old_assembly)
	else:
		print "Wrong file:",trinity_fasta
	return count

def get_duplicates(ncgr_dir,newdir,mmetsp_assemblies):
	id_list = os.listdir(newdir)
	count = 0
	for mmetsp in id_list:
		mmetsp_dir = newdir + mmetsp + "/"
		fastq_list = sorted([s for s in os.listdir(mmetsp_dir) if s.endswith(".fq")])
		if len(fastq_list) > 2:
			#print fastq_list
			count = copy_files(count,ncgr_dir,mmetsp_dir,mmetsp,mmetsp_assemblies)
	print count

newdir = "/mnt/scratch/ljcohen/mmetsp/"
mmetsp_assemblies = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
ncgr_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
clusterfunc.check_dir(newdir)
datafile = "../SraRunInfo_719.csv"
get_duplicates(ncgr_dir,newdir,mmetsp_assemblies)
