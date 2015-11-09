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
	diginorm_string1="python /usr/local/share/khmer/scripts/normalize-by-median.py -p -k 20 "+interleavedir+"*.fq"
	s=subprocess.Popen(diginorm_string1,shell=True)
	s.wait()
	#print diginorm_string1

basedir="/mnt/mmetsp/"
interleavedir="/mnt/mmetsp/subset/trim_combined/interleave/"
diginormdir="/mnt/mmetsp/diginorm/"
clusterfunc.check_dir(diginormdir)
run_diginorm(diginormdir,interleavedir)
