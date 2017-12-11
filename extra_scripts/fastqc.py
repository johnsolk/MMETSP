
import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import glob
# custom Lisa module
import clusterfunc_py3


def fastqc_report(fastq_file_list, newdir, fastqcdir, filename):
    print fastq_file_list
    print fastqcdir + filename
        file_string = str(fastq_file_list)
    # print fastq_file_list
        file_string = " ".join(fastq_file_list)
    # print file_string
        fastqc_string = "fastqc -o " + fastqcdir + " " + file_string
    print "fastqc reports being generated for: " + str(fastq_file_list)
    fastqc_command = [fastqc_string]
    process_name = "fastqc"
    module_name_list = ""
    filename = filename
    clusterfunc_py3.qsub_file(fastqcdir, process_name,
                          module_name_list, filename, fastqc_command)

with open("~/trimmed_files.txt") as 
