import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3
import pickle

def run_streaming_diginorm(trimdir, SRA, diginormdir):
    # from Jessica's streaming protocol:
    diginormfile = diginormdir + SRA + ".stream.diginorm.sh"
    # os.chdir(diginormdir)
    stream_string = """#!/bin/bash
(interleave-reads.py {}{}.trim_1P.fq {}{}.trim_2P.fq && zcat {}orphans.fq.gz)| \\
(trim-low-abund.py -V -k 20 -Z 18 -C 2 - -o - -M 4e9 --diginorm --diginorm-coverage=20) | \\
(extract-paired-reads.py --gzip -p {}{}.paired.gz -s {}{}.single.gz) > /dev/null
""".format(trimdir, SRA, trimdir, SRA, trimdir, diginormdir, SRA, diginormdir, SRA)
    print(stream_string)
    # with open(diginormfile,"w") as diginorm_script:
    #   diginorm_script.write(stream_string)
    #s=subprocess.Popen("sudo bash "+diginormfile,shell=True)
    # s.wait()
    # print "file written:",diginormfile
    # os.chdir("/home/ubuntu/MMETSP/")
    streaming_diginorm_command = [stream_string]
    module_load_list = []
    process_name = "diginorm_stream"
    clusterfunc_py3.qsub_file(diginormdir, process_name,
                          module_load_list, SRA, streaming_diginorm_command)


def interleave_reads(mmetsp_dir, mmetsp):
    interleave_string = """
cd {}
for filename in *.trim_1P.fq
do
	base=$(basename $filename .fq)
	echo $base
	base2=${{base/_1P/_2P}}
	echo $base2
	output=${{base/_1P/}}.interleaved.fq
	#echo $output
	(interleave-reads.py ${{base}}.fq ${{base2}}.fq | gzip > $output)
done
""".format(mmetsp_dir)
    print(interleave_string)
    interleave_command = [interleave_string]
    process_name = "interleave"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = mmetsp
    clusterfunc_py3.qsub_file(mmetsp_dir, process_name,
                              module_name_list, filename, interleave_command)


def run_diginorm(diginormdir, interleavedir, trimdir, sra):
    normalize_median_string = """
normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\
--savegraph {}norm.C20k20.ct \\
-u {}orphans.fq.gz \\
{}*.fq
""".format(diginormdir, trimdir, interleavedir)
    normalize_median_command = [normalize_median_string]
    process_name = "diginorm"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = sra
    clusterfunc_py3.qsub_file(diginormdir, process_name,
                          module_name_list, filename, normalize_median_command)


def run_filter_abund(diginormdir, sra):
    keep_dir = diginormdir + "qsub_files/"
    filter_string = """
filter-abund.py -V -Z 18 {}norm.C20k20.ct {}*.keep
""".format(diginormdir, keep_dir)
    extract_paired_string = extract_paired(diginormdir)
    commands = [filter_string, extract_paired_string]
    process_name = "filtabund"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = sra
    clusterfunc_py3.qsub_file(diginormdir, process_name,
                          module_name_list, filename, commands)

def extract_paired(mmetsp_dir):
    extract_paired_string = """
cd {}qsub_files/
for file in *.abundfilt
do
	extract-paired-reads.py ${{file}}
done
""".format(mmetsp_dir)
    return extract_paired_string

def run_diginorm(mmetsp_dir,mmetsp):
    normalize_median_string = """
normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\
--savegraph {}norm.C20k20.ct \\
-u {}orphans.fq.gz \\
{}*.interleaved.fq
""".format(mmetsp_dir,mmetsp_dir,mmetsp_dir)
    #s=subprocess.Popen("cat diginorm.sh",shell=True)
    # s.wait()
    normalize_median_command = [normalize_median_string]
    process_name = "diginorm"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = mmetsp
    clusterfunc_py3.qsub_file(mmetsp_dir, process_name,
                          module_name_list, filename, normalize_median_command)

def combine_orphaned(mmetsp_dir,item):
    j = """
cd {}qsub_files
rm -rf orphans.keep.abundfilt.fq.gz
gzip -9c orphans.fq.gz.keep.abundfilt > orphans.keep.abundfilt.fq.gz
for file in *.se
do
	gzip -9c ${{file}} >> orphans.keep.abundfilt.fq.gz
done
""".format(mmetsp_dir)
    return j

def rename_pe(mmetsp_dir,item):
    j = """
for file in *trim.interleaved.fq.keep.abundfilt.pe
do
	newfile=${{file%%.fq.keep.abundfilt.pe}}.keep.abundfilt.fq
	cp ${{file}} ${{newfile}}
	gzip ${{newfile}}
done
""".format()
    return j

def split_reads(mmetsp_dir,item):
    split_command="""
for file in *.trim.interleaved.keep.abundfilt.fq.gz
do
   split-paired-reads.py ${{file}}
done
""".format(mmetsp_dir)
    return split_command

def combine(mmetsp_dir,item):
    j="""
cat *.1 > {}{}.left.fq
cat *.2 > {}{}.right.fq
gunzip -c *orphans.keep.abundfilt.fq.gz >> {}{}.left.fq
""".format(mmetsp_dir,item,mmetsp_dir,item,mmetsp_dir,item)
    return j

def consolidate(mmetsp_dir,item):
    combine_orphaned_string = combine_orphaned(mmetsp_dir,item)
    rename_pe_string = rename_pe(mmetsp_dir,item)
    split_reads_string = split_reads(mmetsp_dir,item)
    combine_string = combine(mmetsp_dir,item)
    consolidate_commands=[combine_orphaned_string,rename_pe_string,split_reads_string,combine_string]
    process_name="consolidate"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    clusterfunc_py3.qsub_file(mmetsp_dir,process_name,module_name_list,item,consolidate_commands)

def get_combined_pickle(trim_reads_dir):
    MMETSP_combined = pickle.load(open("MMETSP_combined.dict.pickle", "rb" ))
    return MMETSP_combined

def MMETSP_SRA_conversion(mmetsp):
    mmetsp_metadata = "../SraRunInfo_719.csv"
    with open(mmetsp_metadata, "rU") as metadata:
        headerline = next(metadata).split(',')
        position_mmetsp = headerline.index("SampleName")
        position_sra = headerline.index("Run")
        for line in metadata:
            line_data = line.split(',')
            sra_metadata = line_data[position_sra]
            mmetsp_metadata = line_data[position_mmetsp]
            if mmetsp.endswith("C"):
                mmetsp = mmetsp[:-1]
                print(mmetsp)
            if mmetsp.endswith("_2"):
                mmetsp = mmetsp.split("_")[0]
            if mmetsp_metadata == mmetsp:
                sra = sra_metadata
                print(sra)
                return sra

def make_link(trim_1P,trim_2P,trim_reads_dir,new_dir):
    filename1 = trim_1P.split("/")[-1]
    filename2 = trim_2P.split("/")[-1]
    link_1P = "ln -s " + trim_1P + " " + new_dir + filename1
    link_2P = "ln -s " + trim_2P + " " + new_dir + filename2    
    print(link_1P)
    print(link_2P)
    #s = subprocess.Popen(link_1P, shell=True)
    #s.wait()
    #t = subprocess.Popen(link_2P, shell=True)
    #t.wait()

def execute(basedir, trim_reads_dir):
    MMETSP_combined = get_combined_pickle(trim_reads_dir)
    count = 0
    for species in MMETSP_combined:
        print(species)
        species_count = len(MMETSP_combined[species])
        count += species_count
        new_dir = basedir + species + "/"
        clusterfunc_py3.check_dir(new_dir)
        trimmed_reads = []
        mmetsp_id_list = MMETSP_combined[species]
        for mmetsp in mmetsp_id_list:
            print(mmetsp)
            sra = MMETSP_SRA_conversion(mmetsp)
            trim_1P = trim_reads_dir + sra + ".trim_1P.fq"
            trim_2P = trim_reads_dir + sra + ".trim_2P.fq"	
            if os.path.isfile(trim_1P) and os.path.isfile(trim_2P):
                a = 1
                #print(trim_1P)
                #print(trim_2P)
            else:
                genus = species.split("-")[0]
                species_name = species.split("-")[1]
                genus_species = genus + "_" + species
                if genus_species.startswith("Undescribed"):
                    genus_species = "uncultured_eukaryote"
                    alt_path = "/mnt/scratch/ljcohen/mmetsp_sra/" + genus_species + "/" + sra + "/trim/"
                    trim_1P = alt_path + sra + ".trim_1P.fq"
                    trim_2P = alt_path + sra + ".trim_2P.fq"
                    if os.path.isfile(trim_1P) and os.path.isfile(trim_2P):
                        #print(trim_1P)
                        #print(trim_2P)
                        trim_reads_dir = alt_path
                    else:
                        print("Missing,",trim_1P)
    print("Number of mmetsp id:",count)
            #make_link(trim_1P,trim_2P,trim_reads_dir,new_dir)
            #interleave_reads(new_dir,mmetsp)
            #run_diginorm(mmetsp_dir,item)
            #run_filter_abund(mmetsp_dir, item)
            #consolidate(mmetsp_dir,item)

basedir = "/mnt/scratch/ljcohen/combined/"
trim_reads_dir = "/mnt/scratch/ljcohen/mmetsp_trimmed_reads/"
execute(basedir, trim_reads_dir)
