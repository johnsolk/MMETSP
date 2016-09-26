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
    count = 0
    url_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_ftp = headerline.index("download_path")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            ftp = line_data[position_ftp]
            name_read_tuple = (name, read_type)
            if name_read_tuple in url_data.keys():
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data


def run_busco(busco_dir, trinity_fasta, sample, sra):
    busco_command = """
busco -m trans -in {} \
--cpu 30 -l /mnt/research/ged/lisa/busco/eukaryota -o {}.euk
""".format(trinity_fasta, sample)
    print busco_command
    commands = [busco_command]
    process_name = "busco"
    module_name_list = ""
    filename = sra
    #clusterfunc.qsub_file(busco_dir, process_name,
     #                     module_name_list, filename, commands)


def parse_busco_stats(busco_filename, sample):
    count = 0
    important_lines = [7, 10, 11, 12]
    busco_dict = {}
    busco_dict[sample] = []
    if os.path.isfile(busco_filename):
    	if os.stat(busco_filename).st_size != 0:
        	with open(busco_filename) as buscofile:
            		for line in buscofile:
                		count += 1
                		line_data = line.split()
                		if count in important_lines:
                    			busco_dict[sample].append(int(line_data[0]))
    busco_data = pd.DataFrame.from_dict(busco_dict, orient='index')
    busco_data.columns = ["Complete", "Fragmented", "Missing", "Total"]
    busco_data['Complete_BUSCO_perc'] = busco_data[
        'Complete'] / busco_data['Total']
    return busco_data


def build_DataFrame(data_frame, transrate_data):
    # columns=["sample","Complete","Fragmented","Missing","Total"]
    frames = [data_frame, transrate_data]
    data_frame = pd.concat(frames)
    return data_frame


def execute(data_frame, url_data, basedir):
    trinity_fail = []
    count = 0
    # construct an empty pandas dataframe to add on each assembly.csv to
    for item in url_data.keys():
        print item
        organism = item[0].replace("'","")
	print organism
        sample = "_".join(item).replace("'","")
        org_seq_dir = basedir + organism + "/"
	print org_seq_dir
        url_list = url_data[item]
        for url in url_list:
            sra = basename(urlparse(url).path)
            newdir = org_seq_dir + sra + "/"
            trimdir = newdir + "trim/"
            trinitydir = newdir + "trinity/"
	    busco_dir = newdir + "busco/"
            busco_out_dir = newdir + "busco/qsub_files/"
            clusterfunc.check_dir(busco_dir)
            clusterfunc.check_dir(busco_out_dir)
	    #trinity_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
            trinity_fasta = trinitydir + organism + "_" + sra + ".Trinity.fixed.fasta"
	    busco_file = busco_out_dir + "run_" + sample + \
                ".euk/short_summary_" + sample + ".euk"
            if os.path.isfile(busco_file):
	    #if os.path.isfile(trinity_fasta):
                count += 1
                #run_busco(busco_dir,trinity_fasta,sample,sra)
                data = parse_busco_stats(busco_file, sample)
                data_frame = build_DataFrame(data_frame, data)
            else:
                #print "Trinity failed:", trinity_fasta
                #trinity_fail.append(newdir)
		print "BUSCO has not finished:", busco_file
    print "This is the number of Trinity de novo transcriptome assemblies:"
    print count
    print "This is the number of times Trinity failed:"
    print len(trinity_fail)
    print trinity_fail
    return data_frame

basedir = "/mnt/scratch/ljcohen/mmetsp/"
data_frame = pd.DataFrame()
datafile = "SraRunInfo.csv"    
url_data = get_data(datafile)
print url_data
data_frame = execute(data_frame, url_data, basedir)
data_frame.to_csv("busco_scores.csv")
