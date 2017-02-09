import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3
import pandas as pd

def run_busco(busco_dir,sample,basedir,filename):
    #protists_ensembl
    #eukaryota_odb9
    busco_command = """
python /mnt/home/ljcohen/bin/busco/BUSCO.py \
-i {}{} \
-o {} -l /mnt/home/ljcohen/bin/busco/protists_ensembl \
-m tran --cpu 8
""".format(basedir,filename,sample)
    print(busco_command)
    commands = [busco_command]
    process_name = "busco_protist"
    module_name_list = ""
    filename = sample
    clusterfunc_py3.qsub_file(busco_dir, process_name,module_name_list, filename, commands)


def parse_busco_stats(busco_filename, sample):
    count = 0
    important_lines = [10, 13, 14, 15]
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


def execute(fasta_files,basedir,busco_dir,data_frame):
    count = 0
    # construct an empty pandas dataframe to add on each assembly.csv to
    for filename in fasta_files:
        if filename.startswith("MMETSP"):
            sample= filename.split(".")[0]
            print(sample)
            busco_file = busco_dir + "qsub_files/run_" + sample + "/short_summary_" + sample + ".txt"
            if os.path.isfile(busco_file):
                count += 1
                #run_busco(busco_dir,trinity_fasta,sample,sra)
                data = parse_busco_stats(busco_file, sample)
                data_frame = build_DataFrame(data_frame, data)
            else:
                run_busco(busco_dir,sample,basedir,filename) 
    return data_frame

basedir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"
#basedir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
busco_dir = "/mnt/home/ljcohen/imicrobe_busco/"
data_frame = pd.DataFrame()
fasta_files = os.listdir(basedir)
data_frame = execute(fasta_files,basedir,busco_dir,data_frame)
print("File written: busco_scores.csv")
data_frame.to_csv("busco_scores.csv")
