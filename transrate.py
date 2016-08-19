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
import pandas as pd


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
            if name_read_tuple in url_data.keys():
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def fix_fasta(trinity_fasta,trinity_dir,sample):
	#os.chdir(trinity_dir)
	trinity_out=trinity_dir+sample+".Trinity.fixed.fa"
	fix="""
sed 's_|_-_g' {} > {}
""".format(trinity_fasta,trinity_out)
	#s=subprocess.Popen(fix,shell=True)
	print fix
        #s.wait()
	#os.chdir("/mnt/home/ljcohen/MMETSP/")
	return trinity_out
	
def transrate(trinitydir,transrate_dir,transrate_out,trinity_fasta,sample,trimdir,sra):
	#transrate_command="""
#transrate -o {} --assembly {}
#""".format(transrate_out,trinity_fasta)
	transrate_command="""
transrate --assembly={}{}.Trinity.fixed.fa --threads=27 \
--left={}{}.trim_1P.fq \
--right={}{}.trim_2P.fq \
--output={}
""".format(trinitydir,sample,trimdir,sra,trimdir,sra,transrate_out)
	print transrate_command
	commands = [transrate_command]
        process_name = "transrate"
        module_name_list = ""
        filename = sra
        clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands) 	

def parse_transrate_stats(transrate_assemblies):
        print transrate_assemblies
	if os.stat(transrate_assemblies).st_size != 0:
		data=pd.DataFrame.from_csv(transrate_assemblies,header=0,sep=',')
        	return data

def build_DataFrame(data_frame,transrate_data):
        #columns=["n_bases","gc","gc_skew","mean_orf_percent"]
	frames=[data_frame,transrate_data]
	data_frame=pd.concat(frames)
	return data_frame

def execute(data_frame,url_data,basedir):
	trinity_fail=[]
	count = 0
	# construct an empty pandas dataframe to add on each assembly.csv to
	for item in url_data.keys():
		#print item
		organism=item[0]
		sample="_".join(item)
		org_seq_dir=basedir+organism+"/"
		url_list=url_data[item]
		for url in url_list:
			sra=basename(urlparse(url).path)
			newdir=org_seq_dir+sra+"/"
			trimdir=newdir+"trim/"
			trinitydir=newdir+"trinity/trinity_out/"
			#dammit_dir=trinitydir+"dammit_dir/"
			transrate_dir=newdir+"transrate/"
			clusterfunc.check_dir(transrate_dir)
			#trinity_fasta=dammit_dir+"Trinity.fasta.dammit.fasta"
			trinity_fasta=trinitydir+"Trinity.fasta"
			transrate_out=transrate_dir+"transrate_out."+sample+"/"
			if os.path.isfile(trinity_fasta):
				#transrate(dammit_dir)
		        	#print transrate_out
				count +=1
				#fixed_trinity=fix_fasta(trinity_fasta,trinitydir,sample)
				#transrate(trinitydir,transrate_dir,transrate_out,trinity_fasta,sample,trimdir,sra)
				transrate_assemblies=transrate_out+"assemblies.csv"
				if os.path.isfile(transrate_assemblies):
					data=parse_transrate_stats(transrate_assemblies)
					data_frame=build_DataFrame(data_frame,data)
				else:
					print "Transrate did not complete:",transrate_assemblies
			else:
				print "Trinity failed:",trinity_fasta
				trinity_fail.append(newdir)	
	print "This is the number of Trinity de novo transcriptome assemblies:"
	print count
	print "This is the number of times Trinity failed:"
	print len(trinity_fail)
	print trinity_fail
	return data_frame

basedir = "/mnt/scratch/ljcohen/mmetsp/"	
datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
        "MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]

data_frame=pd.DataFrame()
for datafile in datafiles:
        url_data=get_data(datafile)
        print url_data
        data_frame=execute(data_frame,url_data,basedir)
data_frame.to_csv("transrate_scores.csv")                     
