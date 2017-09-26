import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
import glob
import random
# custom Lisa module
import clusterfunc_py3


def get_dammit_string(trinity_fasta):
    j = """
source /mnt/home/ljcohen/.bashrc
module load GNU/4.8.3
module unload python
module load anaconda
module load parallel
source activate dammit
module load LAST/737
export DAMMIT_DB_DIR=/mnt/research/ged/data/dammitdb/

dammit annotate {} --busco-group eukaryota --n_threads 8
""".format(trinity_fasta)
    return j

def run_dammit(dammit_string,dammitdir,mmetsp,clusterfunc_version):
    dammit_command = [dammit_string]
    process_name = "dammit"
    module_name_list = []
    filename = mmetsp
    #if clusterfunc_version == 1:
    #    print("qml-002")
    #    clusterfunc_py3_1.qsub_file(dammit_dir, process_name, module_name_list, filename, dammit_command)
    #if clusterfunc_version == 2:
    #    print("qml-005")
    #    clusterfunc_py3_2.qsub_file(dammit_dir, process_name, module_name_list, filename, dammit_command)
    #clusterfunc_py3.qsub_file(dammit_dir, process_name, module_name_list, filename, dammit_command)


def execute(finished,missing,assemblies, basedir, dammit_dir):
    num = len(assemblies)
    versions = [1,2]
    submitted = []
    for assembly in assemblies:
        clusterfunc_version = random.choice(versions)
        mmetsp = assembly.split(".")[0]
        print(mmetsp)
        matching = [s for s in missing if mmetsp in s]
        if len(matching) >= 1:
            trinity_fasta = basedir+assembly
            if os.path.isfile(trinity_fasta):
                print(trinity_fasta)
            else:
                print("Assembly missing:",trinity_fasta)
            dammit_string = get_dammit_string(trinity_fasta)
            print(dammit_string)
            #run_dammit(dammit_string, dammit_dir, mmetsp,clusterfunc_version)
            submitted.append(mmetsp)
        else:
            print("Already finished:",mmetsp)
    return submitted

def check_dammit_dirs(dammit_dirs,basedir):
        missing = []
        empty = []
        finished = []
        for i in dammit_dirs:
                mmetsp_dammit_dir = basedir + i + "/"
                files = os.listdir(mmetsp_dammit_dir)
                matching = [s for s in files if ".dammit.fasta" in s]
                if len(matching) >=1:
                        mmetsp_file = mmetsp_dammit_dir + matching[0]
                        if os.stat(mmetsp_file).st_size !=0:
                            print("Finished:"+mmetsp_dammit_dir)
                            finished.append(i)
                        else:
                            print("Empty:"+mmetsp_file)
                            empty.append(mmetsp_dammit_dir)
                else:
                        mmetsp = i.split(".")[0]
                        missing.append(mmetsp)
                        print("Missing:"+mmetsp)
        return missing,empty,finished

dammit_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe_dammit/qsub_files/"
#clusterfunc_py3_1.check_dir(dammit_dir)
files = sorted(os.listdir(dammit_dir))
dammit_dirs = []
for filename in files:
        if filename.startswith("MMETSP"):
                dammit_dirs.append(filename)
#print dammit_dirs
#print len(dammit_dirs)
missing,empty,finished = check_dammit_dirs(dammit_dirs,dammit_dir)
#print missing
#print("Missing:",len(missing))

basedir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"
dammit_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe_dammit/"

assemblies = os.listdir(basedir)

submitted = execute(finished,missing,assemblies, basedir,dammit_dir)
#print(finished)
#print("Finished:",len(finished))
#print("Submitted:",len(submitted))
print("Missing:",len(missing))
print("Empty:",len(empty))
print(empty)
print("Finished:",len(finished))
print("Submitted:",len(submitted))
