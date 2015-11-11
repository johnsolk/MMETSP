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


def run_diginorm(diginormdir,interleavedir):
	print os.listdir(interleavedir)
	os.chdir("/home/ubuntu/khmer/scripts/")
	print os.getcwd()
	with open("diginorm.sh","w") as diginormfile:
		diginormfile.write("sudo python normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\"+"\n")
		diginormfile.write("--savegraph "+diginormdir+"norm.C20k20.ct -u \\"+"\n")
		diginormfile.write(diginormdir+"orphans.fq.gz \\"+"\n")
		diginormfile.write(interleavedir+"*.fq"+"\n")
	s=subprocess.Popen("sudo bash diginorm.sh",shell=True)
	s.wait()
	#s=subprocess.Popen("cat diginorm.sh",shell=True)
	#s.wait()
	os.chdir("/home/ubuntu/MMETSP")

basedir="/mnt/mmetsp/"
interleavedir="/mnt/mmetsp/subset/trim_combined/interleave/"
diginormdir="/mnt/mmetsp/diginorm/"
clusterfunc.check_dir(diginormdir)
run_diginorm(diginormdir,interleavedir)
