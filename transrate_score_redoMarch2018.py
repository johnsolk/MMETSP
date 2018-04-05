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

def transrate(submitted,trinitydir, transrate_dir, transrate_out, trinity_fasta, sample, trimdir, sra, mmetsp):
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
        submitted.append(mmetsp)
        clusterfunc_py3.qsub_file(transrate_dir, process_name,module_name_list, filename, commands)
    else:
        print("trimfiles not present:",trim_1P,trim_2P)
    return submitted

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

def execute(data_frame, mmetsp_data, basedir,assembly_dir,assemblies,transrate_dir):
    finished = []
    submitted = []
    missing = []
    # construct an empty pandas dataframe to add on each assembly.csv to
    special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
    for assembly in assemblies:
        mmetsp = assembly.split(".")[0]
        for item in mmetsp_data.keys():
            sra = item[1]
            organism = item[0].replace("'","")
            org_seq_dir = basedir + organism + "/"
            record_mmetsp = mmetsp_data[item][0]
            if mmetsp not in special_flowers:
                if mmetsp == record_mmetsp:
                    sample = "_".join(item).replace("'","") + "_" + mmetsp
                    print(mmetsp)
                    newdir = org_seq_dir + sra + "/"
                    trimdir = newdir + "trim/"
                    #transrate_dir = newdir + "transrate/"
                    #clusterfunc.check_dir(transrate_dir)
                    trinity_fasta = assembly_dir + assembly
                    transrate_out = transrate_dir + "transrate_out." + mmetsp + "/"
                    transrate_assemblies = transrate_dir + mmetsp + ".assemblies.csv"
                    if os.path.isfile(transrate_assemblies):
                        print("Transrate finished.",transrate_assemblies)
                        finished.append(mmetsp)
                        data = parse_transrate_stats(transrate_assemblies,mmetsp)
                        data_frame = build_DataFrame(data_frame, data)
                    else:
                        print("Running transrate...")
                        submitted = transrate(submitted,assembly_dir,transrate_dir,transrate_out,trinity_fasta,sample,trimdir,sra,mmetsp)
                        transrate_assemblies = transrate_out + "assemblies.csv"
            else:
                print("Special flower:",mmetsp)
    return data_frame,finished,submitted

#assemblydir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
#transrate_dir = "/mnt/research/ged/lisa/mmetsp/mmetsp_transrate_scores/"
#assemblydir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"
#assemblydir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
assemblydir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity_2.2.0_redoMarch2018/"
#transrate_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/transrate_scores_nt/"
transrate_dir = "/mnt/home/ljcohen/mmetsp_redoMarch2018_transrate_scores/"
clusterfunc_py3.check_dir(transrate_dir)
basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
datafile = "SraRunInfo_719.csv"
data_frame = pd.DataFrame()
mmetsp_data = get_data(datafile)
print(mmetsp_data)
assemblies = os.listdir(assemblydir)
print(assemblies)
data_frame,finished,submitted= execute(data_frame, mmetsp_data, basedir, assemblydir,assemblies,transrate_dir)
print("Finished:",len(finished))
print("Submitted:",len(submitted))
print("Total MMETSP id:",len(mmetsp_data.keys()))
print("Data written to file: assembly_evaluation_data/transrate_scores_redoMarch2018.csv")
data_frame.to_csv("assembly_evaluation_data/transrate_scores_redoMarch2018.csv")
