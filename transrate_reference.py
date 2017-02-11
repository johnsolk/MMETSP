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
    #print(transrate_command)
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

def execute(data_frame1, data_frame2, mmetsp_assemblies_dir,mmetsp_2014_assemblies_dir,output_dir1,output_dir2):
    assemblies1 = os.listdir(mmetsp_assemblies_dir)
    assemblies2 = os.listdir(mmetsp_2014_assemblies_dir)
    finished = []
    comparisons = []
    special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
    for item in assemblies1:
        if item.startswith("MMETSP"):
            mmetsp = item.split(".")[0]
            if mmetsp not in special_flowers:
                print(mmetsp)
                reverse_assembly = [s for s in assemblies2 if mmetsp in s.split("_") or s.split("_")[-1].startswith(mmetsp)]
                if len(reverse_assembly)==0:
                    print("Assembly not present:",mmetsp,mmetsp_2014_assemblies_dir)
                else:
                    #print(reverse_assembly)
                    reverse_trinity_fasta = mmetsp_2014_assemblies_dir + reverse_assembly[0]
                    trinity_fasta = mmetsp_assemblies_dir + item
                    #reference_filename = mmetsp_assemblies+mmetsp+".nt.fa.fixed.fa"
                    #reference_filename = mmetsp_assemblies+mmetsp+".cds.fa.fixed.fa" 
                    if os.path.isfile(trinity_fasta):
                        #print("MMETSP assembly found:", trinity_fasta)
                        comparisons.append(trinity_fasta)
                        transrate_assemblies_ref = output_dir1 + mmetsp + ".assemblies.csv"
                        transrate_reverse_assemblies = output_dir2 + mmetsp + ".assemblies.csv"
                        if os.path.isfile(transrate_assemblies_ref):
                            print("Finished:",transrate_assemblies_ref)
                            data1 = parse_transrate_stats(transrate_assemblies_ref,mmetsp,mmetsp)
                            data_frame1 = build_DataFrame(data_frame1, data1)
                        else:
                            print("Running...")
                            transrate(output_dir1, mmetsp, trinity_fasta, mmetsp_2014_assemblies_dir, reverse_trinity_fasta)
                        if os.path.isfile(transrate_reverse_assemblies):
                            print("Finished:",transrate_reverse_assemblies)
                            data2 = parse_transrate_stats(transrate_reverse_assemblies,mmetsp,mmetsp)
                            data_frame2 = build_DataFrame(data_frame2, data2)
                        else:
                            print("Running reverse...")
                            transrate_reverse(output_dir2, mmetsp, trinity_fasta, mmetsp_2014_assemblies_dir, reverse_trinity_fasta)
                    else:
                        print("Missing:",reference_filename)
            else:
                print("Special flower:",mmetsp)
                #fix_command = "sed 's_|_-_g' "+mmetsp_assemblies+mmetsp+".nt.fa > "+mmetsp_assemblies+mmetsp+".nt.fa.fixed.fa"
                 #print fix_command
                 #u = subprocess.Popen(fix_command, shell=True, stdout=PIPE)
            #u.wait()
    print("Comparisons:",len(comparisons))
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

#mmetsp_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
#mmetsp_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"

mmetsp_2014_assemblies_dir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.3.2/"
mmetsp_assemblies_dir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0_zenodo/"
#mmetsp_2014_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"


output_dir1 = "/mnt/home/ljcohen/mmetsp_transrate_reference_dib-trinity2.2.0_v_trinity2.3.2/"
output_dir2 = "/mnt/home/ljcohen/mmetsp_transrate_reference_trinity2.3.2_v_dib-trinity2.2.0/"

#output_dir1 = "/mnt/home/ljcohen/mmetsp_transrate_reference_dib-trinity2.2.0_v_ncgr/"
#output_dir2 = "/mnt/home/ljcohen/mmetsp_transrate_reference_ncgr_v_dib-trinity2.2.0/"
clusterfunc_py3.check_dir(output_dir1)
clusterfunc_py3.check_dir(output_dir2)

#output_dir1 = "/mnt/home/ljcohen/mmetsp_transrate_reference_dib-trinity2.2.0_v_dib-trinity2014/"
#output_dir2 = "/mnt/home/ljcohen/mmetsp_transrate_reference_dib-trinity2014_v_trinity2.2.0/"

data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()

data_frame1, data_frame2 = execute(data_frame1, data_frame2, mmetsp_assemblies_dir,mmetsp_2014_assemblies_dir,output_dir1,output_dir2)
data_frame1.to_csv("assembly_evaluation_data/transrate_reference_trinity2.2.0_v_trinity2.3.2.csv")
data_frame2.to_csv("assembly_evaluation_data/transrate_reverse_trinity2014_v_trinity2.3.2.csv")
print("Reference scores written.")
print("Reverse reference scores written.")
