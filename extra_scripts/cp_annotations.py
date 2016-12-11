import os
import subprocess
from subprocess import Popen, PIPE


def check_dammit_dirs(dammit_dirs,basedir):
	missing = []
	complete = []
	for i in dammit_dirs:
		mmetsp_dammit_dir = basedir + i
		files = os.listdir(mmetsp_dammit_dir)
		matching = [s for s in files if ".dammit.fasta" in s]
		if len(matching) >=1:
			print "Finished:",mmetsp_dammit_dir
			complete.append(i)
		else:
			missing.append(i)
			print "Missing:",i	 
	return missing,complete


def copy_files(complete,basedir):
	fasta_dir = "/mnt/research/ged/lisa/dammit_annotations/fasta/"
	gff_dir = "/mnt/research/ged/lisa/dammit_annotations/gff/"
	for j in complete:
		mmetsp = j.split(".")[0]
		dammit_dir = basedir + j
		fasta_file = dammit_dir+"/"+j+".fasta"
		gff_file = dammit_dir+"/"+j+".gff3"
		copy_string1 = "cp "+fasta_file+" "+fasta_dir
		copy_string2 = "cp "+gff_file+" "+gff_dir
		print copy_string1
		print copy_string2
		s = subprocess.Popen(copy_string1, shell=True)
    		s.wait()
		t = subprocess.Popen(copy_string2, shell=True)
		t.wait()

basedir = "/mnt/home/ljcohen/mmetsp_dammit/qsub_files/"
files = sorted(os.listdir(basedir))
dammit_dirs = []
for filename in files:
	if filename.startswith("MMETSP"):
		dammit_dirs.append(filename)
print dammit_dirs
print len(dammit_dirs)
missing,complete = check_dammit_dirs(dammit_dirs,basedir)
print missing
print "Missing:",len(missing)
copy_files(complete,basedir)
