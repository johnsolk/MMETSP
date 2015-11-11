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

def run_filter_abund(diginormdir):
	print os.listdir(diginormdir)
	os.chdir("/home/ubuntu/khmer/scripts/")
	with open("trim.sh","w") as trimfile:
		trimfile.write("sudo python filter-abund.py -V -Z 18 "+diginormdir+"norm.C20k20.ct "+diginormdir+"*.keep && \\"+"\n")
		trimfile.write("rm "+diginormdir+"*.keep "+diginormdir+"norm.C20k20.ct"+"\n")
	s=subprocess.Popen("sudo bash trim.sh",shell=True)
	s.wait()
	#s=subprocess.Popen("cat trim.sh",shell=True)
	#s.wait()
	os.chdir("/home/ubuntu/MMETSP/")


def rename_files(diginormdir):
	print os.listdir(diginormdir)
	os.chdir("/home/ubuntu/khmer/scripts/")
	with open("rename.sh","w") as renamefile:
		renamefile.write("for file in "+diginormdir+"*.pe.*.abundfilt"+"\n")
		renamefile.write("do"+"\n")
		renamefile.write("\textract-paired-reads.py ${file} && \\"+"\n")
		renamefile.write("\t\trm ${file}"+"\n")
		renamefile.write("done"+"\n")
	s=subprocess.Popen("cat rename.sh",shell=True)
	s.wait()
	os.chdir("/home/ubuntu/MMETSP/")


def run_diginorm(diginormdir,interleavedir):
	print os.listdir(interleavedir)
	os.chdir("/home/ubuntu/khmer/scripts/")
	print os.getcwd()
	with open("diginorm.sh","w") as diginormfile:
		diginormfile.write("sudo python normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\"+"\n")
		diginormfile.write("--savegraph "+diginormdir+"norm.C20k20.ct -u \\"+"\n")
		diginormfile.write("/mnt/mmetsp/subset/trim_combined/orphans.fq.gz \\"+"\n")
		diginormfile.write(interleavedir+"*.fq"+"\n")
	s=subprocess.Popen("sudo bash diginorm.sh",shell=True)
	s.wait()
	#s=subprocess.Popen("cat diginorm.sh",shell=True)
	#s.wait()
	os.chdir("/home/ubuntu/MMETSP/")

def combine_orphaned():
	gzip -9c orphans.fq.gz.keep.abundfilt > orphans.keep.abundfilt.fq.gz && \
    rm orphans.fq.gz.keep.abundfilt
for file in *.pe.*.abundfilt.se
do
   gzip -9c ${file} >> orphans.keep.abundfilt.fq.gz && \
        rm ${file}
done



basedir="/mnt/mmetsp/"
interleavedir="/mnt/mmetsp/subset/trim_combined/interleave/"
diginormdir="/mnt/mmetsp/diginorm/"
clusterfunc.check_dir(diginormdir)
#run_diginorm(diginormdir,interleavedir)
#run_filter_abund(diginormdir)
rename_files(diginormdir)
