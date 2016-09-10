import os
import os.path
from os.path import basename
from urllib import urlopen
from urlparse import urlparse
import subprocess
from subprocess import Popen, PIPE
import urllib
import shutil
import glob
# custom Lisa module
import clusterfunc
# Python plotting libraries
import pandas as pd


def get_data(thefile):
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
            # print name_read_tuple
            # check to see if Scientific Name and run exist
            if name_read_tuple in mmetsp_data.keys():
                # check to see if ftp exists
                if mmetsp in mmetsp_data[name_read_tuple]:
                    print "mmetsp ID already exists:", mmetsp
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
    # print fix
    # s.wait()
    # os.chdir("/home/ubuntu/MMETSP/")
    return trinity_out


def fix_fasta_reference(mmetsp_assembly, mmetsp_assembly_dir):
    mmetsp_assembly_out = mmetsp_assembly_dir + mmetsp_assembly + ".fixed.fa"
    fix = """
sed 's_|_-_g' {}{} > {}
""".format(mmetsp_assembly_dir, mmetsp_assembly, mmetsp_assembly_out)
    # print fix
    # s=subprocess.Popen(fix,shell=True)
    # s.wait()
    return mmetsp_assembly_out


def transrate(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, trinity_fasta, filename)
    print transrate_command
    commands = [transrate_command]
    process_name = "trans_ref"
    module_name_list = ""
    filename = sample
    # clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)


def transrate_reverse(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, filename, trinity_fasta)
    print "This is the reverse transrate command:"
    print transrate_command
    commands = [transrate_command]
    process_name = "trans_ref_reverse"
    module_name_list = ""
    filename = sample
    # clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)


def parse_transrate_stats(transrate_assemblies):
    data = pd.DataFrame.from_csv(transrate_assemblies, header=0, sep=',')
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
                    print transrate_contigs
                    data = parse_transrate_stats(transrate_contigs)
                    data_frame = build_DataFrame(data_frame, data)
                else:
                    print "File missing:", transrate_contigs
    return data_frame


def execute(data_frame1, data_frame2, mmetsp_data, basedir, mmetsp_assemblies):
    trinity_fail = []
    reference_filename = "blank"
    # construct an empty pandas dataframe to add on each assembly.csv to
    for item in mmetsp_data.keys():
        # print item
        organism = item[0]
        sample = "_".join(item)
        org_seq_dir = basedir + organism + "/"
        mmetsp_list = mmetsp_data[item]
        for mmetsp in mmetsp_list:
            print mmetsp
            assemblyfileslist = os.listdir(mmetsp_assemblies)
            for filename in assemblyfileslist:
                if filename.startswith(mmetsp):
                    if filename.endswith(".fixed.fa"):
                        print "This is not the one you want."
                    else:
                        print "MMETSP assembly found:", filename
                        reference_filename = filename
            if reference_filename == "blank":
                print "No MMETSP file found:", mmetsp
                break
            else:
                sra = item[1]
                newdir = org_seq_dir + sra + "/"
                trinitydir = newdir + "trinity/"
                transrate_dir = newdir + "transrate/"
                transrate_reference_dir = newdir + "transrate_dib_v_ncgr_cds/"
                clusterfunc.check_dir(transrate_reference_dir)
                transrate_reverse_dir = newdir + "transrate_ncgr_cds_v_dib/"
                clusterfunc.check_dir(transrate_reverse_dir)
                trinity_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
                if os.path.isfile(trinity_fasta):
                    print trinity_fasta
                    fixed_mmetsp_ref = fix_fasta_reference(
                        reference_filename, mmetsp_assemblies)
                    transrate(transrate_reference_dir, sample, trinity_fasta,
                              mmetsp_assemblies_dir, fixed_mmetsp_ref)
                    transrate_reverse(
                        transrate_reverse_dir, sample, trinity_fasta, mmetsp_assemblies_dir, fixed_mmetsp_ref)
                else:
                    print "Trinity failed:", newdir
                    trinity_fail.append(newdir)
                transrate_assemblies_ref = transrate_reference_dir + sample + "/assemblies.csv"
                transrate_reverse_assemblies = transrate_reverse_dir + sample + "/assemblies.csv"
                print transrate_assemblies_ref
                print transrate_reverse_assemblies
                if os.path.isfile(transrate_assemblies_ref):
                    data1 = parse_transrate_stats(transrate_assemblies_ref)
                    data_frame1 = build_DataFrame(data_frame1, data1)
                if os.path.isfile(transrate_reverse_assemblies):
                    data2 = parse_transrate_stats(transrate_reverse_assemblies)
                    data_frame2 = build_DataFrame(data_frame2, data2)
    print "This is the number of times Trinity failed:"
    print len(trinity_fail)
    print trinity_fail
    return data_frame1, data_frame2


def get_assemblies_data(data_frame, transrate_dir):
    listofdirs = os.listdir(transrate_dir)
    for dirname in listofdirs:
        transrate_assemblies = transrate_dir + dirname + "/assemblies.csv"
        print transrate_assemblies
        if os.path.isfile(transrate_assemblies):
            data = parse_transrate_stats(transrate_assemblies)
            data_frame = build_DataFrame(data_frame, data)
        else:
            print "File missing:", transrate_assemblies
    return data_frame


def get_ref_transrate(transrate_dir):
    listdirs = os.listdir(transrate_dir)
    print listdirs
    for dirname in listdirs:
        newdir = transrate_dir + dirname + "/"
        print newdir
        newfile = newdir + "assemblies.csv"
        if os.path.isfile(newfile):
            print "Exists:", newfile
        else:
            print "Does not exist:", newfile

basedir = "/mnt/scratch/ljcohen/mmetsp/"
mmetsp_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"
datafiles = ["MMETSP_SRA_Run_Info_subset_msu1.csv", "MMETSP_SRA_Run_Info_subset_msu2.csv", "MMETSP_SRA_Run_Info_subset_msu3.csv", "MMETSP_SRA_Run_Info_subset_msu4.csv",
             "MMETSP_SRA_Run_Info_subset_msu5.csv", "MMETSP_SRA_Run_Info_subset_msu6.csv", "MMETSP_SRA_Run_Info_subset_msu7.csv"]

data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()
for datafile in datafiles:
    url_data = get_data(datafile)
    print url_data
    data_frame1, data_frame2 = execute(
        data_frame1, data_frame2, url_data, basedir, mmetsp_assemblies_dir)
data_frame1.to_csv("transrate_reference_scores_cds.csv")
data_frame2.to_csv("transrate_reverse_scores_cds.csv")
