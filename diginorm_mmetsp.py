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

def get_data(thefile):
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
        #print headerline        
        position_name=headerline.index("ScientificName")
        position_reads=headerline.index("Run")
        position_ftp=headerline.index("download_path")
        for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            read_type=line_data[position_reads]
            ftp=line_data[position_ftp]
            name_read_tuple=(name,read_type)
            print name_read_tuple
            #check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                #check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def run_filter_abund(diginormdir):
	if glob.glob(diginormdir+"*keep.abundfilt*"):
		print "filter-abund.py already run"
	else:
		os.chdir(diginormdir)
		with open("filter_abund.sh","w") as abundfile:
			abundfile.write("sudo python /home/ubuntu/khmer/scripts/filter-abund.py -V -Z 18 "+diginormdir+"norm.C20k20.ct "+diginormdir+"*.keep"+"\n")
			#trimfile.write("rm "+diginormdir+"*.keep "+diginormdir+"norm.C20k20.ct"+"\n")
		s=subprocess.Popen("sudo bash filter_abund.sh",shell=True)
		s.wait()
		#s=subprocess.Popen("cat trim.sh",shell=True)
		#s.wait()
		os.chdir("/home/ubuntu/MMETSP/")

def run_streaming_diginorm():
# from Jessica's streaming protocol:
	stream_string="""#!/bin/bash
zcat orphans.fq.gz && trim-low-abund.py \\
-V -k 20 -Z 18 -C 3 - -o - -M 4e9 --diginorm \\
--diginorm-coverage=20 | extract-paired-reads.py \\
--gzip -p paired.gz -s single.gz
""".format()
	with open("diginorm.sh","w") as diginorm_script:
		diginorm_script.write(stream_string)

def rename_files(diginormdir):
	if glob.glob(diginormdir+"*.abundfilt.pe"):
		print "paired reads already extracted"
	else:
		os.chdir(diginormdir)
		with open("rename.sh","w") as renamefile:
			renamefile.write("for file in *.abundfilt"+"\n")
			renamefile.write("do"+"\n")
			renamefile.write("\tpython /home/ubuntu/khmer/scripts/extract-paired-reads.py ${file} && \\"+"\n")
			renamefile.write("\t\trm ${file}"+"\n")
			renamefile.write("done"+"\n")
		#s=subprocess.Popen("cat rename.sh",shell=True)
		#s.wait()
		s=subprocess.Popen("sudo bash rename.sh",shell=True)
		s.wait()
		os.chdir("/home/ubuntu/MMETSP/")

def run_diginorm(diginormdir,interleavedir):
	# this will create and run a script from the working directory
	# output *.keep files will be in the working directory
	if glob.glob(diginormdir+"*keep*"):
		print "normalize-by-median.py already run"
	else:
		os.chdir(diginormdir)
		with open("diginorm.sh","w") as diginormfile:
			diginormfile.write("sudo python /home/ubuntu/khmer/scripts/normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\"+"\n")
			diginormfile.write("--savegraph "+diginormdir+"norm.C20k20.ct -u \\"+"\n")
			diginormfile.write("/mnt/mmetsp/subset/trim/orphans.fq.gz \\"+"\n")
			diginormfile.write(interleavedir+"*.fq"+"\n")
		s=subprocess.Popen("sudo bash diginorm.sh",shell=True)
		s.wait()
		#s=subprocess.Popen("cat diginorm.sh",shell=True)
		#s.wait()
		os.chdir("/home/ubuntu/MMETSP/")

def combine_orphaned(diginormdir):
	if glob.glob(diginormdir+"orphans.keep.abundfilt.fq.gz"):
		print "orphan reads already combined"
	else:
		os.chdir(diginormdir)
		print "combinding orphans now..."
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
	print "renaming pe files now..."
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

def execute(basedir,url_data):
	for item in url_data.keys():
		organism=item[0]
		seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
        	clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
			SRA=basename(urlparse(url).path)
			newdir=org_seq_dir+SRA+"/"
			interleavedir=newdir+"interleave/"
			diginormdir=newdir+"diginorm/"
			clusterfunc.check_dir(diginormdir)
			#run_diginorm(diginormdir,interleavedir)
			#run_filter_abund(diginormdir)
			#rename_files(diginormdir)
			combine_orphaned(diginormdir)
			rename_pe(diginormdir)	

basedir="/mnt/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset2.csv"
url_data=get_data(datafile)
execute(basedir,url_data)

