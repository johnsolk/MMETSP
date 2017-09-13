import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3
import pandas as pd


def fix_fasta(trinity_fasta, trinity_dir, sample):
    # os.chdir(trinity_dir)
    trinity_out = trinity_dir + sample + ".Trinity.fixed.fa"
    fix = """
sed 's_|_-_g' {} > {}
""".format(trinity_fasta, trinity_out)
    # s=subprocess.Popen(fix,shell=True)
    print(fix)
    # s.wait()
    # os.chdir("/mnt/home/ljcohen/MMETSP/")
    return trinity_out

def transrate(trinitydir, transrate_dir, transrate_out, trinity_fasta, sample, trimdir, sra, mmetsp):
    trim_1P = trimdir + sra + ".trim_1P.fq"
    trim_2P = trimdir + sra + ".trim_2P.fq"
    if os.path.isfile(trim_1P) and os.path.isfile(trim_2P):
        transrate_command = """
transrate --assembly={} --threads=8 \
--left={}{}.trim_1P.fq \
--right={}{}.trim_2P.fq \
--output=/tmp/transrate_out.{}
cp /tmp/transrate_out.{}/assemblies.csv {}{}.assemblies.csv
rm -rf /tmp/transrate_out.{}
""".format(trinity_fasta, trimdir, sra, trimdir, sra, sample,sample,transrate_dir,mmetsp,sample)
        print(transrate_command)
        commands = [transrate_command]
        process_name="transrate"
        module_name_list = ""
        filename = mmetsp
        clusterfunc_py3.qsub_file(transrate_dir, process_name,module_name_list, filename, commands)
    else:
        print("trimfiles not present:",trim_1P,trim_2P)

def parse_transrate_stats(transrate_assemblies,mmetsp):
    print(transrate_assemblies)
    if os.stat(transrate_assemblies).st_size != 0:
        data = pd.DataFrame.from_csv(transrate_assemblies, header=0, sep=',')
        data['SampleName'] = mmetsp
        return data

def build_DataFrame(data_frame, transrate_data):
    # columns=["n_bases","gc","gc_skew","mean_orf_percent"]
    frames = [data_frame, transrate_data]
    data_frame = pd.concat(frames)
    return data_frame

def execute(data_frame, accessions, basedir,assembly_dir,assemblies,transrate_dir):
    # construct an empty pandas dataframe to add on each assembly.csv to
    for accession in accessions:    
        # print item
        seq_dir = basedir + accession + "/"
        assembly = [s for s in assemblies if s.startswith(accession) and s.endswith(".fasta")]
        if len(assembly)==0:
            print("Assembly not present:",assembly)
        else:
            print(assembly)
            trimdir = seq_dir + "trim/"
            #transrate_dir = newdir + "transrate/"
            #clusterfunc.check_dir(transrate_dir)
            trinity_fasta = assembly_dir + assembly[0]
            transrate_out = transrate_dir + "transrate_out." + accession + "/"
            transrate_assemblies = transrate_dir + accession + ".assemblies.csv"
            if os.path.isfile(transrate_assemblies):
                print("Transrate finished.",transrate_assemblies)
                data = parse_transrate_stats(transrate_assemblies,accession)
                data_frame = build_DataFrame(data_frame, data)
            else:
                print("Running transrate...")
                transrate(assembly_dir,transrate_dir,transrate_out,trinity_fasta,accession,trimdir,accession,accession)
                transrate_assemblies = transrate_out + "assemblies.csv"
    return data_frame

macmanes_assemblies_dir = "/mnt/home/ljcohen/oysterriver_assemblies/MacManes/orthomerged/"
dib_assemblies_dir = "/mnt/home/ljcohen/oysterriver_assemblies/finished/"
accessions = "DRR053698, DRR082659, ERR489297, DRR030368, DRR031870, DRR046632, DRR069093, ERR058009, ERR1016675, SRR2086412, SRR3499127, SRR1789336, SRR2016923, ERR1674585, DRR036858"
accessions = accessions.replace(" ","").split(",")
print(accessions)
print(len(accessions),"accessions")
basedir = "/mnt/scratch/ljcohen/oysterriver/"

#assemblydir = "/mnt/home/ljcohen/oysterriver_assemblies/finished/"
#transrate_dir = "/mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_dib/"
#clusterfunc_py3.check_dir(transrate_dir)
assemblydir = "/mnt/home/ljcohen/oysterriver_assemblies/MacManes/orthomerged/"
transrate_dir = "/mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_macmanes/"

basedir = "/mnt/scratch/ljcohen/oysterriver/"
data_frame = pd.DataFrame()
assemblies = os.listdir(assemblydir)
data_frame= execute(data_frame, accessions,basedir, assemblydir,assemblies,transrate_dir)
#print("Data written to file: /mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_dib.csv")
#data_frame.to_csv("/mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_dib.csv")
print("Data written to file: /mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_macmanes.csv")
data_frame.to_csv("/mnt/home/ljcohen/oysterriver_assemblies/transrate_scores_macmanes.csv")
