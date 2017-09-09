import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3


def combine_orphans(diginormdir):
    diginorm_files_dir = diginormdir + "qsub_files/"
    rename_orphans = """
gzip -9c {}orphans.fq.gz.keep.abundfilt > {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
        gzip -9c ${{file}} >> {}orphans.keep.abundfilt.fq.gz
done
""".format(diginorm_files_dir, diginormdir, diginorm_files_dir, diginormdir)
    return rename_orphans


def rename_files(trinitydir, diginormdir, diginormfile, SRA):
    # takes diginormfile in,splits reads and put into newdir
    rename_orphans = combine_orphans(diginormdir)
    split_paired = "split-paired-reads.py -d " + diginormdir + " " + diginormfile
    rename_string1 = "cat " + diginormdir + "*.1 > " + trinitydir + SRA + ".left.fq"
    rename_string2 = "cat " + diginormdir + \
        "*.2 > " + trinitydir + SRA + ".right.fq"
    rename_string3 = "gunzip -c " + diginormdir + \
        "orphans.keep.abundfilt.fq.gz >> " + trinitydir + SRA + ".left.fq"
    commands = [rename_orphans, split_paired,
                rename_string1, rename_string2, rename_string3]
    process_name = "rename"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = SRA
    clusterfunc_py3.qsub_file(diginormdir,process_name,module_name_list,filename,commands)


def run_trinity(trinitydir,left,right,mmetsp):
    trinity_command = """
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out_2.2.0.Trinity.fasta ]; then exit 0 ; fi
Trinity --left {} \\
--right {} --output /tmp/{}.trinity_out_2.2.0 --full_cleanup --seqType fq --max_memory 50G --CPU 16
cp /tmp/{}.trinity_out_2.2.0.Trinity.fasta /mnt/home/ljcohen/oysterriver_assemblies/
rm -rf /tmp/{}.trinity_out_2.2.0*
""".format(trinitydir, left, right, mmetsp, mmetsp,mmetsp)
    commands = [trinity_command]
    process_name = "trinity_2.2.0"
    module_name_list = ["trinity/2.2.0"]
    filename = mmetsp
    clusterfunc_py3.qsub_file(trinitydir, process_name,
                          module_name_list, filename, commands)


def check_trinity(seqdir, SRA, count):
    trinity_dir = seqdir + "trinity/"
    trinity_file = trinity_dir + "trinity_out/Trinity.fasta"
    if os.path.isfile(trinity_file) == False:
        if os.path.isdir(trinity_dir) == False:
            print("Still need to run.", trinity_dir)
            run_trinity(trinity_dir, SRA)
            count += 1
        else:
            print("Incomplete:", trinity_dir)
            run_trinity(trinity_dir, SRA)
            count += 1
    return count


def fix_fasta(trinity_fasta, trinity_dir, sample):
    os.chdir(trinity_dir)
    trinity_out = trinity_dir + sample + ".Trinity.fixed.fasta"
    fix = """
sed 's_|_-_g' {} > {}
""".format(trinity_fasta, trinity_out)
    s = subprocess.Popen(fix, shell=True)
    print(fix)
    s.wait()
    os.chdir("/mnt/home/ljcohen/MMETSP/")
    return trinity_out


def execute(accession,basedir):
        seq_dir = basedir + accession + "/"
        diginormdir = seq_dir + "diginorm/"
        diginormfile = diginormdir + "qsub_files/" + accession + \
                ".trimmed.interleaved.fq.keep.abundfilt.pe"
        trinitydir = seq_dir + "trinity/"
        trinity_fasta = trinitydir + accession + ".Trinity.fixed.fasta"
        clusterfunc_py3.check_dir(trinitydir)
        trinity_files = os.listdir(trinitydir)
        print(trinity_files)
        if os.path.isfile(trinity_fasta) == False:
            if os.path.isfile(diginormfile):
                print("file exists:",diginormfile)
                #rename_files(trinitydir,diginormdir,diginormfile,accession)
            else:
                print("diginorm file does not exist?",diginormfile)
            right = [s for s in trinity_files if s.endswith(".right.fq")][0]
            left = [s for s in trinity_files if s.endswith(".left.fq")][0]
            right = trinitydir + right
            left = trinitydir + left
            print(left)
            print(right)
            if os.path.isfile(left) and os.path.isfile(right):
                run_trinity(trinitydir,left,right,accession)
            else:
                print("No files:",left)
            #    print "Trinity completed successfully.", trinity_fasta
            #    count += 1
            #    assemblydir = "/mnt/scratch/ljcohen/oysterriver_assemblies/"
            #    copy_string = "cp " + trinity_fasta + " " + assemblydir
            #    print copy_string
                #s = subprocess.Popen(copy_string, shell=True)
                #s.wait()
                #trinity_out=fix_fasta(trinity_fasta,trinitydir,sample)

accessions = "DRR053698, DRR082659, ERR489297, DRR030368, DRR031870, DRR046632, DRR069093, ERR058009, ERR1016675, SRR2086412, SRR3499127, SRR1789336, SRR2016923, ERR1674585, DRR036858"
accessions = accessions.replace(" ","").split(",")
print(accessions)
print(len(accessions),"accessions")
basedir = "/mnt/scratch/ljcohen/oysterriver/"
clusterfunc_py3.check_dir(basedir)
for accession in accessions:
   execute(accession,basedir)
