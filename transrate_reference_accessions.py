import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import os
from os import path
# custom Lisa module
import clusterfunc_py3
# Python plotting libraries
import pandas as pd


	
def transrate(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o /tmp/{}_forw \\
--assembly {} \\
--reference {} \\
--threads 8
cp /tmp/{}_forw/assemblies.csv {}{}.assemblies.csv
rm -rf /tmp/{}_forw*
""".format(sample, trinity_fasta, filename,sample,transrate_dir,sample,sample)
    commands = [transrate_command]
    process_name = "trans_ref"
    module_name_list = ""
    filename = sample
    print(transrate_command)
    clusterfunc_py3.qsub_file(mmetsp_assemblies_dir,process_name,module_name_list,filename,commands)

def transrate_reverse(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o /tmp/{}_rev \\
--assembly {} \\
--reference {} \\
--threads 8
cp /tmp/{}_rev/assemblies.csv {}{}.assemblies.csv
rm -rf /tmp/{}_rev*
""".format(sample, filename,trinity_fasta,sample,transrate_dir,sample,sample)
    #print("This is the reverse transrate command:")
    commands = [transrate_command]
    process_name = "trans_ref_reverse"
    module_name_list = ""
    filename = sample
    print(transrate_command)
    clusterfunc_py3.qsub_file(mmetsp_assemblies_dir,process_name,module_name_list,filename,commands)

def parse_transrate_stats(transrate_assemblies,sra,mmetsp):
    data = pd.DataFrame.from_csv(transrate_assemblies, header=0, sep=',')
    data['SampleName'] = mmetsp
    data['Run'] = sra
    return data

def build_DataFrame(data_frame, transrate_data):
    # columns=["n_bases","gc","gc_skew","mean_orf_percent"]
    frames = [data_frame, transrate_data]
    data_frame = pd.concat(frames)
    return data_frame

def get_contigs_data(data_frame, transrate_dir):
    listofdirs = os.listdir(transrate_dir)
    for dirname in listofdirs:
        transrate_dirname = transrate_dir + dirname + "/"
        transrate_dirnames = os.listdir(transrate_dirname)
        for dirname2 in transrate_dirnames:
            if dirname2.endswith(".fixed"):
                transrate_contigs = transrate_dirname + dirname2 + "/contigs.csv"
                if os.path.isfile(transrate_contigs):
                    print(transrate_contigs)
                    data = parse_transrate_stats(transrate_contigs)
                    data_frame = build_DataFrame(data_frame, data)
                else:
                    print("File missing:", transrate_contigs)
    return data_frame

def execute(data_frame1, data_frame2, query_assemblies_dir,reference_assemblies_dir,output_dir1,output_dir2):
    assemblies1 = os.listdir(query_assemblies_dir)
    assemblies2 = os.listdir(reference_assemblies_dir)
    print(assemblies1)
    print(assemblies2)
    for item in assemblies1:
        if item.endswith(".fasta"):
            sra_id = item.split(".")[0]
            print(sra_id)
            reverse_assembly = [s for s in assemblies2 if sra_id in s.split("_") or s.split("_")[-1].startswith(sra_id)]
            if len(reverse_assembly)==0:
                print("Assembly not present:",sra_id,reference_assemblies_dir)
            else:
                print(reverse_assembly)
                reverse_trinity_fasta = reference_assemblies_dir + reverse_assembly[0]
                trinity_fasta = query_assemblies_dir + item
                if os.path.isfile(trinity_fasta):
                    print("SRA assembly found:", trinity_fasta)
                    transrate_assemblies_ref = output_dir1 + sra_id + ".assemblies.csv"
                    transrate_reverse_assemblies = output_dir2 + sra_id + ".assemblies.csv"
                    if os.path.isfile(transrate_assemblies_ref):
                        print("Finished:",transrate_assemblies_ref)
                        data1 = parse_transrate_stats(transrate_assemblies_ref,sra_id,sra_id)
                        data_frame1 = build_DataFrame(data_frame1, data1)
                    else:
                        print("Running...")
                        transrate(output_dir1, sra_id, trinity_fasta, reference_assemblies_dir, reverse_trinity_fasta)
                    if os.path.isfile(transrate_reverse_assemblies):
                        print("Finished:",transrate_reverse_assemblies)
                        data2 = parse_transrate_stats(transrate_reverse_assemblies,sra_id,sra_id)
                        data_frame2 = build_DataFrame(data_frame2, data2)
                    else:
                        print("Running reverse...")
                        transrate_reverse(output_dir2, sra_id, trinity_fasta, reference_assemblies_dir, reverse_trinity_fasta)
    return data_frame1,data_frame2

		
def get_assemblies_data(data_frame, transrate_dir):
    listofdirs = os.listdir(transrate_dir)
    for dirname in listofdirs:
        transrate_assemblies = transrate_dir + dirname + "/assemblies.csv"
        print(transrate_assemblies)
        if os.path.isfile(transrate_assemblies):
            data = parse_transrate_stats(transrate_assemblies)
            data_frame = build_DataFrame(data_frame, data)
        else:
            print("File missing:", transrate_assemblies)
    return data_frame

def get_ref_transrate(transrate_dir):
    listdirs = os.listdir(transrate_dir)
    print(listdirs)
    for dirname in listdirs:
        newdir = transrate_dir + dirname + "/"
        print(newdir)
        newfile = newdir + "assemblies.csv"
        if os.path.isfile(newfile):
            print("Exists:", newfile)
        else:
            print("Does not exist:", newfile)


macmanes_assemblies_dir = "/mnt/home/ljcohen/oysterriver_assemblies/MacManes/orthomerged/"
dib_assemblies_dir = "/mnt/home/ljcohen/oysterriver_assemblies/finished/"

output_dir1 = "/mnt/home/ljcohen/oysterriver_assemblies/dib_v_macmanes/"
output_dir2 = "/mnt/home/ljcohen/oysterriver_assemblies/macmanes_v_dib/"
clusterfunc_py3.check_dir(output_dir1)
clusterfunc_py3.check_dir(output_dir2)

data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()

data_frame1, data_frame2 = execute(data_frame1, data_frame2, dib_assemblies_dir,macmanes_assemblies_dir,output_dir1,output_dir2)
data_frame1.to_csv("/mnt/home/ljcohen/oysterriver_assemblies/transrate_reference_dib_v_macmanes.csv")
data_frame2.to_csv("/mnt/home/ljcohen/oysterriver_assemblies/transrate_reverse_ref_macmanes_v_dib.csv")
print("Reference scores written: /mnt/home/ljcohen/oysterriver_assemblies/transrate_reference_dib_v_macmanes.csv")
print("Reverse reference scores written: /mnt/home/ljcohen/oysterriver_assemblies/transrate_reverse_ref_macmanes_v_dib.csv")
