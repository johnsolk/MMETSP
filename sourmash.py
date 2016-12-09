import fnmatch
import os
import os.path
# custom Lisa module
import clusterfunc_py3

def get_head_command(SRA, full_filename, filename):
    head_command="""
head -4000000 {} > /mnt/scratch/ljcohen/mmetsp_sourmash/{}.head
""".format(full_filename,filename)
    commands = [head_command]
    process_name = "head"
    module_name_list = [""]
    filename = SRA
    #clusterfunc.qsub_file("/mnt/scratch/ljcohen/mmetsp_sourmash/",
    #                          process_name, module_name_list, filename, commands)

def get_sourmash_command(mmetsp):
    sourmash_command="""
sourmash compute --dna --protein /mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/{}.trinity_out_2.2.0.Trinity.fasta -k 21 --name-from-first
""".format(mmetsp)
    commands = [sourmash_command]
    process_name = "sourmash"
    module_name_list = [""]
    filename = mmetsp
    clusterfunc_py3.qsub_file("/mnt/home/ljcohen/mmetsp_sourmash/",process_name, module_name_list, filename, commands)

def execute(basedir, files):
    for fasta_file in files:
        mmetsp = fasta_file.split(".")[0]
        get_sourmash_command(mmetsp)
	
basedir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
files = os.listdir(basedir)
execute(basedir, files)
