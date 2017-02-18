import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
import glob
# custom Lisa module
import clusterfunc_py3


def get_dammit_string(trinity_fasta):
    j = """
dammit annotate {} --busco-group eukaryota --n_threads 14
""".format(trinity_fasta)
    return j

def run_dammit(dammit_string,dammitdir,mmetsp):
    dammit_command = [dammit_string]
    process_name = "dammit"
    module_name_list = []
    filename = mmetsp
    #clusterfunc_py3.qsub_file(dammit_dir, process_name, module_name_list, filename, dammit_command)

def execute(assemblies, basedir, dammit_dir):
    for assembly in assemblies:
        mmetsp = assembly.split(".")[0]
        print(mmetsp)
        trinity_fasta = basedir+assembly
        print(trinity_fasta)
        dammit_string = get_dammit_string(trinity_fasta)
        run_dammit(dammit_string, dammit_dir, mmetsp)

basedir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
dammit_dir = "/mnt/home/ljcohen/mmetsp_dammit/"
assemblies = os.listdir(basedir)
execute(assemblies, basedir,dammit_dir)
