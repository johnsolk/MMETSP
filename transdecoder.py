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

def transdecoder_LongOrf(transdecoderdir,trinity_fasta):
	os.chdir(transdecoderdir)
	print os.getcwd()
        print os.path.isfile(trinity_fasta)
	if os.path.isfile(trinity_fasta):
		print "file exists:",trinity_fasta
		trans_command="""
/home/ubuntu/bin/TransDecoder-3.0.0/TransDecoder.LongOrfs -t {} -m 100
""".format(trinity_fasta)
		print trans_command	
		s=subprocess.Popen(trans_command,shell=True)
		s.wait()
		print "Transdecoder finished."
	os.chdir("/home/ubuntu/MMETSP/")

def transdecoder_Predict(transdecoderdir,trinity_fasta_prefix):
	os.chdir(transdecoderdir)
	print os.getcwd()
	print os.path.isfile(trinity_fasta_prefix)
	trans_predict_command="""
/home/ubuntu/bin/TransDecoder-3.0.0/TransDecoder.Predict -t {}
""".format(trinity_fasta_prefix)
	print trans_predict_command
	os.chdir("/home/ubuntu/MMETSP/")
	s=subprocess.Popen(trans_predict_command,shell=True)
        s.wait()

def get_longest_ORF(transdecoderdir,trinity_fasta):
	os.chdir(transdecoderdir)
	get_longest_orf_command="""
/home/ubuntu/bin/TransDecoder-3.0.0/util/get_longest_ORF_per_transcript.pl {}.transdecoder.pep > {}.transdecoder.pep.longest.pep
""".format(trinity_fasta,trinity_fasta)
	print get_longest_orf_command
	os.chdir("/home/ubuntu/MMETSP/")
	s=subprocess.Popen(get_longest_orf_command,shell=True)
        s.wait()

def fix(transdecoderdir,trinity_fasta):
	fix_command="""
sed -e 's/>.*::SRR/>SRR/' {}{}.longest.pep | sed -e 's/::.*//' | sed 's/\*//g'
""".format(transdecoderdir,trinity_fasta)
	print fix_command
	s=subprocess.Popen(fix_command,shell=True)
        s.wait()

def gather_counts(salmondir):
        os.chdir(salmondir)
        gather_counts="python /home/ubuntu/MMETSP/gather-counts.py"
        print os.getcwd()
        print gather_counts
        #s=subprocess.Popen(gather_counts,shell=True)
        #s.wait()
        os.chdir("/home/ubuntu/MMETSP/")

def copy_files(trinity_fasta,transdecoderdir):
        #copy_command="cp "+trinity_fasta+" "+transdecoderdir
        #print copy_command
        rm_command="rm -rf "+transdecoderdir+trinity_fasta+".transdecoder_dir"
	print rm_command
	s=subprocess.Popen(rm_command,shell=True)
        s.wait()

def execute(url_data):
	for item in url_data.keys():
		organism=item[0]
		org_seq_dir=basedir+organism+"/"
		url_list=url_data[item]
		for url in url_list:
			sra=basename(urlparse(url).path)
			newdir=org_seq_dir+sra+"/"
			trinitydir=newdir+"trinity/trinity_out/"
			transdecoderdir=newdir+"transdecoder/"
			clusterfunc.check_dir(transdecoderdir)
			trinity_fasta=trinitydir+sra+".Trinity.fixed.fa"
			trinity_fasta_prefix=sra+".Trinity.fixed.fa"
			transdecoder_LongOrf(transdecoderdir,trinity_fasta_prefix)
			transdecoder_Predict(transdecoderdir,trinity_fasta_prefix)
			get_longest_ORF(transdecoderdir,trinity_fasta_prefix)
			fix(transdecoderdir,trinity_fasta_prefix)
                        #copy_files(trinity_fasta_prefix,transdecoderdir)

basedir="/mnt/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset_g.csv"
url_data=get_data(datafile)
print url_data
execute(url_data)
