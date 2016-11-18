import os

def check_lists(new,old):
	missing = []
	for i in old:
		if i not in new:
			missing.append(i) 
	return missing

def fix_new(new):
	fixed_new = []
	for i in new:
		mmetsp = i.split(".")
		fixed_new.append(mmetsp[0])	
	return fixed_new

basedir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
mmetsp_dir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "../SraRunInfo_719.csv"
new = os.listdir(basedir)
fixed_new = fix_new(new)
print len(fixed_new)
old = os.listdir(mmetsp_dir)
print len(old)
missing = check_lists(fixed_new,old)
print "Missing:",len(missing)
print missing
