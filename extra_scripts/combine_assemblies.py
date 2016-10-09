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
import pandas as pd
# custom Lisa module
import clusterfunc

def get_trinity(trinitydir, left, right, SRA):
    trinity_command = """
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
#if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi
Trinity --left {} \\
--right {} --output {}trinity_out --seqType fq --JM 20G --CPU 16
""".format(trinitydir, trinitydir, trinitydir, trinitydir, left, right, trinitydir)
    commands = [trinity_command]
    process_name = "trinity"
    module_name_list = ["trinity/20140413p1"]
    filename = SRA
    clusterfunc.qsub_file(trinitydir, process_name,
                          module_name_list, filename, commands)

def combine_orphans(diginormdir,mmetsp):
	diginorm_files_dir = diginormdir + "qsub_files/"
    	rename_orphans = """
touch {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
        gzip -9c ${{file}} >> {}orphans.keep.abundfilt.fq.gz
done
""".format(diginormdir,diginorm_files_dir, diginormdir)
	commands = [rename_orphans]
        process_name = "orphans"
        module_name_list = ["GNU/4.8.3", "khmer/2.0"]
        filename = mmetsp
        clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)

def split_paired_reads(trinitydir, diginormdir, mmetsp):
	diginorm_files_dir = diginormdir + "qsub_files/"
	listoffiles = os.listdir(diginorm_files_dir)
	for digi_filename in listoffiles:
		if digi_filename.endswith(".pe"):
    			split_paired = "split-paired-reads.py -d " + diginormdir + " " + diginorm_files_dir + digi_filename
    			commands = [split_paired]
    			process_name = "split"
    			module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    			filename = mmetsp
    			clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)

def rename_files(trinitydir, diginormdir, mmetsp):
	rename_string1 = "cat " + diginormdir + "*.1 > " + trinitydir + "/" + mmetsp + ".left.fq"
        rename_string2 = "cat " + diginormdir + "*.2 > " + trinitydir + "/" + mmetsp + ".right.fq"
        rename_string3 = "gunzip -c " + diginormdir + "orphans.keep.abundfilt.fq.gz >> " + trinitydir + mmetsp + ".left.fq"
        commands = [rename_string1, rename_string2, rename_string3]
        process_name = "rename"
        module_name_list = ["GNU/4.8.3", "khmer/2.0"]
        filename = mmetsp
 	clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)


def interleave_reads(fastq_list,mmetsp_dir, mmetsp, diginormdir):
	for i in range(0,len(fastq_list),2):
		print i
		left = fastq_list[i]
		print left
		right = fastq_list[i+1]
		print right
		interleave_file = diginormdir + left.split(".")[0] + ".interleaved.fq" 
        	interleave_string = "interleave-reads.py " + mmetsp_dir + left + " " + mmetsp_dir + right + " > " + interleave_file
        	print interleave_string
        	interleave_command = [interleave_string]
        	process_name = "interleave"
        	module_name_list = ["GNU/4.8.3", "khmer/2.0"]
        	filename = left.split(".")[0]
        	clusterfunc.qsub_file(diginormdir, process_name,
                              module_name_list, filename, interleave_command)

def run_normalize_by_median(diginormdir, mmetsp):
    normalize_median_string = """
normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\
--savegraph {}norm.C20k20.ct \\
{}*.fq
""".format(diginormdir, diginormdir)
    normalize_median_command = [normalize_median_string]
    process_name = "diginorm"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = mmetsp
    clusterfunc.qsub_file(diginormdir, process_name,
                          module_name_list, filename, normalize_median_command)

def extract_paired():
    extract_paired_string = """
for file in *.abundfilt
do
        extract-paired-reads.py ${{file}}
done
""".format()
    return extract_paired_string

def run_filter_abund(diginormdir, mmetsp):
    keep_dir = diginormdir + "qsub_files/"
    filter_string = """
filter-abund.py -V -Z 18 {}norm.C20k20.ct {}*.keep
""".format(diginormdir, keep_dir)
    extract_paired_string = extract_paired()
    commands = [filter_string, extract_paired_string]
    process_name = "filtabund"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = mmetsp
    clusterfunc.qsub_file(diginormdir, process_name,
                          module_name_list, filename, commands)

def run_diginorm(fastq_list,mmetsp_dir,mmetsp):
	diginormdir = mmetsp_dir + "diginorm/"
	clusterfunc.check_dir(diginormdir)
	#interleave_reads(fastq_list,mmetsp_dir,mmetsp,diginormdir)
	#run_normalize_by_median(diginormdir,mmetsp)
	#run_filter_abund(diginormdir, mmetsp)


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

def run_Trinity(ncgr_dir,mmetsp_dir,mmetsp,data_frame1,data_frame2):
	trinitydir = mmetsp_dir + "trinity/"
	clusterfunc.check_dir(trinitydir)
	diginormdir = mmetsp_dir + "diginorm/"
	transratedir = mmetsp_dir + "transrate/"
	clusterfunc.check_dir(transratedir)
	#split_paired_reads(trinitydir, diginormdir, mmetsp)
	#combine_orphans(diginormdir,mmetsp)
	right = trinitydir + mmetsp + ".right.fq"
	left = trinitydir + mmetsp + ".left.fq"
	trinity_fasta = trinitydir + "trinity_out/" + "Trinity.fasta"
	#rename_files(trinitydir, diginormdir, mmetsp)
	if os.path.isfile(right) and os.path.isfile(left):
		if os.path.isfile(trinity_fasta):
			print trinity_fasta
			cp_string = "cp " + trinity_fasta + " " + mmetsp_dir + mmetsp + ".Trinity.fasta"
			fixed_fasta = fix_fasta(trinity_fasta, mmetsp_dir,mmetsp) 
			#print cp_string
			old_assemblies = sorted([s for s in os.listdir(mmetsp_dir) if s.endswith(".fixed.fasta") and s.split("_")[-1].startswith("SRR")])
			#print old_assemblies 
			#for old_assembly in old_assemblies:
				#transrate(transratedir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly)
				#transrate_reverse(transratedir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly)
			#	sra = old_assembly.split("_")[-1].split(".")[0]
			#	sample = mmetsp + "_" + sra
    			#	reverse_sample = "reverse_" + mmetsp + "_" + sra
			#	transrate_assemblies_ref = transratedir + sample + "/assemblies.csv"
        		#	transrate_reverse_assemblies = transratedir + reverse_sample + "/assemblies.csv"
				#if os.path.isfile(transrate_assemblies_ref):
				#	data1 = parse_transrate_stats(transrate_assemblies_ref,sra,mmetsp)
				#	data_frame1 = build_DataFrame(data_frame1,data1)
				#else:
				#	"Transrate failed:",transrate_assemblies_ref
				#if os.path.isfile(transrate_reverse_assemblies):
				#	data2 = parse_transrate_stats(transrate_reverse_assemblies,sra,mmetsp)
				#	data_frame2 = build_DataFrame(data_frame2,data2)

				#else:
				#	print "Reverse failed:",transrate_reverse_assemblies
				#s = subprocess.Popen(cp_string, shell = True)
				#s.wait()
			ncgr_assembly = mmetsp + ".nt.fa.fixed.fa"
			sample = mmetsp + "_" + mmetsp
			reverse_sample = "reverse_" + mmetsp + "_" + mmetsp
			transrate(transratedir, mmetsp, fixed_fasta, ncgr_dir, ncgr_assembly)
                        transrate_reverse(transratedir, mmetsp, fixed_fasta, ncgr_dir, ncgr_assembly)

			transrate_assemblies_ref = transratedir + sample + "/assemblies.csv"
                        transrate_reverse_assemblies = transratedir + reverse_sample + "/assemblies.csv"
 			if os.path.isfile(transrate_assemblies_ref):
                        	data1 = parse_transrate_stats(transrate_assemblies_ref,mmetsp,mmetsp)
                                data_frame1 = build_DataFrame(data_frame1,data1)
                        else:
                                print "Transrate failed:",transrate_assemblies_ref
                        if os.path.isfile(transrate_reverse_assemblies):
                                data2 = parse_transrate_stats(transrate_reverse_assemblies,mmetsp,mmetsp)
                                data_frame2 = build_DataFrame(data_frame2,data2)
			else:
				print "Transrate failed:",transrate_reverse_assemblies
		else:
			get_trinity(trinitydir, left, right, mmetsp)
			#cp_string1 = "cp " + right + " " + mmetsp_dir 
			#cp_string2 = "cp " + left + " " + mmetsp_dir
			#s = subprocess.Popen(cp_string1, shell=True)
    			#print cp_string1
    			#s.wait()
			#t = subprocess.Popen(cp_string2, shell=True)
			#print cp_string2
			#t.wait()	
	return data_frame1,data_frame2

def fix_fasta(trinity_fasta, mmetsp_dir, sample):
	# os.chdir(trinity_dir)
	trinity_out = mmetsp_dir + sample + ".Trinity.fixed.fasta"
	fix = """
sed 's_|_-_g' {} > {}
""".format(trinity_fasta, trinity_out)
	#s=subprocess.Popen(fix,shell=True)
	#print fix
        #s.wait()
	return trinity_out

def transrate(transrate_dir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly):
    sra = old_assembly.split("_")[-1].split(".")[0]
    sample = mmetsp + "_" + sra
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {}{} \\
--threads 8
""".format(transrate_dir, sample, fixed_fasta, mmetsp_dir,old_assembly)
    commands = [transrate_command]
    process_name = "trans_ref"
    module_name_list = ""
    filename = mmetsp
    #print transrate_command
    #s = subprocess.Popen(transrate_command, shell=True)
    #s.wait()
    #clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)

def transrate_reverse(transrate_dir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly):
    sra = old_assembly.split("_")[-1].split(".")[0]
    sample = "reverse_" + mmetsp + "_" + sra
    transrate_command = """
transrate -o {}{} \\
--assembly {}{} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, mmetsp_dir,old_assembly,fixed_fasta)
    print "This is the reverse transrate command:"
    commands = [transrate_command]
    process_name = "trans_ref_reverse"
    module_name_list = ""
    filename = sample
    #print transrate_command
    #s = subprocess.Popen(transrate_command, shell=True)
    #s.wait()
    #clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)


def get_duplicates(ncgr_dir,newdir,data_frame1,data_frame2):
	id_list = os.listdir(newdir)
	for mmetsp in id_list:
		mmetsp_dir = newdir + mmetsp + "/"
		fastq_list = sorted([s for s in os.listdir(mmetsp_dir) if s.endswith(".fq")])
		if len(fastq_list) > 2:
			print fastq_list
			#run_diginorm(fastq_list,mmetsp_dir,mmetsp)	
			data_frame1,data_frame2 = run_Trinity(ncgr_dir,mmetsp_dir,mmetsp,data_frame1,data_frame2)
	return data_frame1,data_frame2

newdir = "/mnt/scratch/ljcohen/mmetsp/"
ncgr_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
clusterfunc.check_dir(newdir)
datafile = "../SraRunInfo_719.csv"
#move_files(url_data,basedir,newdir)
data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()
data_frame1,data_frame2 = get_duplicates(ncgr_dir,newdir,data_frame1,data_frame2)
data_frame1.to_csv("../assembly_evaluation_data/ncgr_combined_transrate_reference.csv")
data_frame2.to_csv("../assembly_evaluation_data/ncgr_combined_transrate_reverse.csv")
print "Reference scores written: ../ncgr_combined_transrate_reference.csv"
print "Reverse reference scores written: ../ncgr_combined_transrate_reverse.csv"
