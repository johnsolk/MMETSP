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
		renamefile.write("for file in "+diginormdir+"*.abundfilt"+"\n")
		renamefile.write("do"+"\n")
		renamefile.write("\tpython extract-paired-reads.py ${file} && \\"+"\n")
		renamefile.write("\t\trm ${file}"+"\n")
		renamefile.write("done"+"\n")
	#s=subprocess.Popen("cat rename.sh",shell=True)
	#s.wait()
	s=subprocess.Popen("sudo bash rename.sh",shell=True)
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

def combine_orphaned(diginormdir):
	print os.listdir(diginormdir)
	with open("combine_orphaned.sh","w") as combinedfile:
		combinedfile.write("gzip -9c "+diginormdir+"orphans.fq.gz.keep.abundfilt > "+diginormdir+"orphans.keep.abundfilt.fq.gz && \\"+"\n")
		combinedfile.write("\trm "+diginormdir+"orphans.fq.gz.keep.abundfilt"+"\n")
		combinedfile.write("for file in "+diginormdir+"*.se"+"\n")
		combinedfile.write("do"+"\n")
		combinedfile.write("\tgzip -9c ${file} >> orphans.keep.abundfilt.fq.gz && \\"+"\n")
        	combinedfile.write("\t\trm ${file}"+"\n")
		combinedfile.write("done"+"\n")
	#s=subprocess.Popen("cat combine_orphaned.sh",shell=True)
	#s.wait()
	s=subprocess.Popen("sudo bash combine_orphaned.sh",shell=True)
	s.wait()
	
def rename_pe(diginormdir):
	with open("rename.sh","w") as renamefile:
		renamefile.write("for file in "+diginormdir+"*trimmed.interleaved.fq.keep.abundfilt.pe"+"\n")
		renamefile.write("do"+"\n")
   		renamefile.write("\tnewfile=${file%%.fq.keep.abundfilt.pe}.keep.abundfilt.fq"+"\n")
   		renamefile.write("\tmv ${file} ${newfile}"+"\n")
   		renamefile.write("\tgzip ${newfile}"+"\n")
		renamefile.write("done"+"\n")
	#s=subprocess.Popen("cat rename.sh",shell=True)
	#s.wait()
	s=subprocess.Popen("sudo bash rename.sh",shell=True)	
	s.wait()

basedir="/mnt/mmetsp/"
interleavedir="/mnt/mmetsp/subset/trim_combined/interleave/"
diginormdir="/mnt/mmetsp/diginorm/"
clusterfunc.check_dir(diginormdir)
#run_diginorm(diginormdir,interleavedir)
# want to see more about the naming of the output files
# outputs files to /home/ubuntu/khmer/scripts/
# mv /home/ubuntu/khmer/scripts/*keep* /mnt/mmetsp/diginorm/ 
#run_filter_abund(diginormdir)
# outputs files to /home/ubuntu/khmer/scripts
# mv /home/ubuntu/khmer/scripts/*.abundfilt /mnt/mmetsp/diginorm/  
#rename_files(diginormdir)
# this will output files to /home/ubuntu/khmer/scripts
# 11/12/2015 there is a problem with Exception: no paired reads!? check file formats...
# check in ~/MMETSP
# mv /home/ubuntu/khmer/scripts/orphans.* /mnt/mmetsp/diginorm/
# mv /home/ubuntu/khmer/scripts/*keep* /mnt/mmetsp/diginorm/
#combine_orphaned(diginormdir)
rename_pe(diginormdir)
