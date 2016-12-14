import os
import subprocess
from subprocess import Popen, PIPE


def check_dirs(dirs,basedir):
	missing = []
	complete = []
	for i in dirs:
		mmetsp_dir = basedir + i
		files = os.listdir(mmetsp_dir)
		matching = [s for s in files if "assemblies.csv" in s]
		if len(matching) >=1:
			print "Finished:",mmetsp_dir
			complete.append(i)
		else:
			missing.append(i)
			print "Missing:",i	 
	return missing,complete


def copy_files(complete,basedir):
	transrate_dir = "/mnt/home/ljcohen/mmetsp_transrate_scores/"
	for j in complete:
		mmetsp = j.split("_")[-1]
		dir = basedir + j
		csv_file = dir+"/"+"assemblies.csv"
		copy_string1 = "cp "+csv_file+" "+transrate_dir+mmetsp+".assemblies.csv"
		print copy_string1
		s = subprocess.Popen(copy_string1, shell=True)
    		s.wait()

basedir = "/mnt/scratch/ljcohen/mmetsp_transrate_trinity2.2.0/"
files = sorted(os.listdir(basedir))
transrate_dirs = []
for filename in files:
	if filename.startswith("transrate_out"):
		transrate_dirs.append(filename)
print transrate_dirs
print len(transrate_dirs)
missing,complete = check_dirs(transrate_dirs,basedir)
print missing
print "Missing:",len(missing)
copy_files(complete,basedir)
