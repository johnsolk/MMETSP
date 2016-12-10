import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3
import pandas as pd


def get_data(thefile):
    count = 0
    mmetsp_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_mmetsp = headerline.index("SampleName")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            mmetsp = line_data[position_mmetsp]
            test_mmetsp = mmetsp.split("_")
            if len(test_mmetsp) > 1:
                mmetsp = test_mmetsp[0]
            name_read_tuple = (name, read_type)
            if name_read_tuple in mmetsp_data.keys():
                if mmetsp in mmetsp_data[name_read_tuple]:
                    print("url already exists:", ftp)
                else:
                    mmetsp_data[name_read_tuple].append(mmetsp)
            else:
                mmetsp_data[name_read_tuple] = [mmetsp]
        return mmetsp_data


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
transrate --assembly={} --threads=14 \
--left={}{}.trim_1P.fq \
--right={}{}.trim_2P.fq \
--output={}
""".format(trinity_fasta, trimdir, sra, trimdir, sra, transrate_out)
        print(transrate_command)
        commands = [transrate_command]
        process_name="transrate"
        module_name_list = ""
        filename = mmetsp
        clusterfunc_py3.qsub_file(transrate_dir, process_name,module_name_list, filename, commands)
    else:
        print("trimfiles not present:",trim_1P,trim_2P)

def parse_transrate_stats(transrate_assemblies):
    print(transrate_assemblies)
    if os.stat(transrate_assemblies).st_size != 0:
        data = pd.DataFrame.from_csv(transrate_assemblies, header=0, sep=',')
        return data

def build_DataFrame(data_frame, transrate_data):
    # columns=["n_bases","gc","gc_skew","mean_orf_percent"]
    frames = [data_frame, transrate_data]
    data_frame = pd.concat(frames)
    return data_frame

def execute(data_frame, mmetsp_data, basedir,assembly_dir,assemblies,transrate_dir):
    # construct an empty pandas dataframe to add on each assembly.csv to
    special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
    for item in mmetsp_data.keys():
        # print item
        sra = item[1]
        organism = item[0].replace("'","")
        org_seq_dir = basedir + organism + "/"
        mmetsp = mmetsp_data[item][0]
        if mmetsp not in special_flowers:
            sample = "_".join(item).replace("'","") + "_" + mmetsp
            print(mmetsp)
            mmetsp_assembly = [s for s in assemblies if s.startswith(mmetsp)]
            if len(mmetsp_assembly)==0:
                print("Assembly not present:",mmetsp_assembly)
            else:
                print(mmetsp_assembly)
                newdir = org_seq_dir + sra + "/"
                trimdir = newdir + "trim/"
                #transrate_dir = newdir + "transrate/"
                #clusterfunc.check_dir(transrate_dir)
                trinity_fasta = assembly_dir + mmetsp_assembly[0]
                transrate_out = transrate_dir + "transrate_out." + sample + "/"
                transrate_assemblies = transrate_out + "assemblies.csv"
                if os.path.isfile(transrate_assemblies):
                    data = parse_transrate_stats(transrate_assemblies)
                    data_frame = build_DataFrame(data_frame, data)
                else:
                    print("Running transrate...")
                    transrate(assembly_dir,transrate_dir,transrate_out,trinity_fasta,sample,trimdir,sra,mmetsp)
                    transrate_assemblies = transrate_out + "assemblies.csv"
        else:
            print("Special flower:",mmetsp)
    return data_frame

assemblydir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
transrate_dir = "/mnt/scratch/ljcohen/mmetsp_transrate_trinity2.2.0/"
basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
datafile = "SraRunInfo.csv"
data_frame = pd.DataFrame()
mmetsp_data = get_data(datafile)
print(mmetsp_data)
assemblies = os.listdir(assemblydir)
data_frame = execute(data_frame, mmetsp_data, basedir, assemblydir,assemblies,transrate_dir)
#data_frame.to_csv("transrate_scores.csv")
