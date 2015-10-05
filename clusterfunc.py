# Lisa Cohen
# commonly-used functions
# to use, "import cluster"

import os
import subprocess
from subprocess import Popen, PIPE

def check_dir(dirname):
    if os.path.isdir(dirname)==False:
        os.mkdir(dirname)
        print "Directory created:",dirname

def get_sge_filename(basedir,process_name,filename):
    sge_dir=basedir+"sge_files/"
    check_dir(sge_dir)
    sge_filename=sge_dir+process_name+"_"+filename+".sge"
    return sge_dir,sge_filename

def get_module_load_list(module_name_list):
    module_list=[]
    for module in module_name_list:
        module_load="module load "+module
        module_list.append(module_load)
    return module_list

def qsub_sge_file(basedir,process_name,module_name_list,filename,process_string,threads):
    working_dir=os.getcwd()
    sge_dir,sge_filename=get_sge_filename(basedir,process_name,filename)
    os.chdir(sge_dir)
    module_load=get_module_load_list(module_name_list)
    with open(sge_filename,"w") as sge_file:
         sge_file.write("#!/bin/bash\n")
         sge_file.write("#$ -S /bin/bash\n")
         sge_file.write("#$ -cwd\n")
         sge_file.write("#$ -M lisa.cohen@nyumc.org\n")
         sge_file.write("#$ -m ae\n")
         # use this for bedtools (igv module):
         if any('bedtools' in s for s in module_load):
             sge_file.write('module unload gcc/4.4\n')
         for module_string in module_load:
             sge_file.write(module_string+"\n")
             #print module_string
         for string in process_string:
             sge_file.write(string+"\n")
             print string
    #qsub_string="qsub -q tcga.q -pe threaded "+threads+" "+sge_filename
    qsub_string="qsub -pe threaded "+str(threads)+" "+sge_filename
    #qsub_string="qsub -q highmem.q -pe threaded "+threads+" "+sge_filename
    print qsub_string
    s=subprocess.Popen(qsub_string,shell=True)
    s.wait()
    os.chdir(working_dir)
