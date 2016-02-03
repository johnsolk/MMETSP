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

def fix_fasta(trinity_fasta,trinity_dir,sample):
	os.chdir(trinity_dir)
	trinity_out=trinity_dir+sample+".Trinity.fixed.fa"
	fix="""
sed 's_|_-_g' {} > {}
""".format(trinity_fasta,trinity_out)
	s=subprocess.Popen(fix,shell=True)
        s.wait()
	os.chdir("/home/ubuntu/MMETSP/")
	return trinity_out
	
def transrate(trinitydir,transrate_out,trinity_fasta):
	transrate_command="""
transrate -o {} --assembly {}
""".format(transrate_out,trinity_fasta)
	s=subprocess.Popen(transrate_command,shell=True)
	s.wait()

def execute(url_data,basedir):
	trinity_fail=[]
	for item in url_data.keys():
		print item
		organism=item[0]
		sample="_".join(item)
		org_seq_dir=basedir+organism+"/"
		url_list=url_data[item]
		for url in url_list:
			sra=basename(urlparse(url).path)
			newdir=org_seq_dir+sra+"/"
			trinitydir=newdir+"trinity/trinity_out/"
			dammit_dir=trinitydir+"dammit_dir/"
			transrate_dir=newdir+"transrate/"
			clusterfunc.check_dir(transrate_dir)
			#trinity_fasta=dammit_dir+"Trinity.fasta.dammit.fasta"
			trinity_fasta=trinitydir+"Trinity.fasta"
			transrate_out=transrate_dir+sample
			if os.path.isfile(trinity_fasta):
				#transrate(dammit_dir)
		        	fixed_trinity=fix_fasta(trinity_fasta,trinitydir,sample)
				transrate(trinitydir,transrate_out,fixed_trinity)
			else:
				print "Trinity failed:",newdir
				trinity_fail.append(newdir)	
	print "This is the number of times Trinity failed:"
	print len(trinity_fail)
	print trinity_fail

# basedir:datafile
file_locations={"/mnt/mmetsp/":"MMETSP_SRA_Run_Info_subset_d.csv",
		"/mnt/mmetsp1/mmetsp/":"MMETSP_SRA_Run_Info_subset_a.csv",
		"/mnt/mmetsp2/mmetsp/":"MMETSP_SRA_Run_Info_subset_b.csv"}
#datafile="MMETSP_SRA_Run_Info_subset2.csv"
for basedir in file_locations.keys():
	datafile=file_locations[basedir]
	url_data=get_data(datafile)
	print url_data
	execute(url_data,basedir)
