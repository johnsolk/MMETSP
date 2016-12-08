import os

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

basedir = "/mnt/home/ljcohen/imicrobe_dammit/qsub_files/"
files = sorted(os.listdir(basedir))
dammit_dirs = []
for filename in files:
	if filename.startswith("MMETSP"):
		dammit_dirs.append(filename)
print dammit_dirs
print len(dammit_dirs)
missing,complete = check_dammit_dirs(dammit_dirs,basedir)
print complete
print "Complete:",len(complete)
