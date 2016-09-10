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
import yaml
# custom Lisa module
import clusterfunc

def get_data(thefile):
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
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
            if name_read_tuple in url_data.keys():
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def get_quant_file(salmondir,sra):
	quant_file = salmondir+sra+".quant"
	return quant_file

def get_config_file(quant_file,rapclustdir,sra):
	config_file=rapclustdir+sra+"_config.yaml"
	out_dir=rapclustdir+sra+"_rapclust_out"
	yaml_dict={"conditions":[sra],"samples":{sra:[quant_file]},"outdir":out_dir}
	yaml_dump=yaml.dump(yaml_dict)
	with open(config_file,"w") as config_file:
		config_file.write(yaml_dump)
	return config_file

def run_rap_clust(salmondir,rapclustdir,sra):
	quant_file=get_quant_file(salmondir,sra)
	config_file=get_config_file(quant_file,rapclustdir,sra)
	config_filename=rapclustdir+sra+"_config.yaml"
	rapclust_string="RapClust --config "+str(config_filename)
	print rapclust_string
	commands=[rapclust_string]
	process_name="rapclust"
	module_name_list=""
	filename=sra
	clusterfunc.qsub_file(rapclustdir,process_name,module_name_list,filename,commands)

def execute(url_data):
        for item in url_data.keys():
                organism=item[0]
                org_seq_dir=basedir+organism+"/"
                url_list=url_data[item]
                for url in url_list:
                        sra=basename(urlparse(url).path)
                        newdir=org_seq_dir+sra+"/"
                        salmondir=newdir+"salmon/"
			rapclustdir=newdir+"rapclust/"
			clusterfunc.check_dir(rapclustdir)
                        clusterfunc.check_dir(salmondir)
			run_rap_clust(salmondir,rapclustdir,sra)

basedir="/mnt/scratch/ljcohen/mmetsp/"
datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
        "MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]
for datafile in datafiles:
        url_data=get_data(datafile)
        print url_data
        execute(url_data)
