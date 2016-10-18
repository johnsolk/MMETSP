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

def fix_fasta(trinity_fasta, trinity_dir, sample):
    	trinity_out = trinity_dir + sample + ".Trinity.fixed.fasta"
	if os.path.isfile(trinity_out):
		print "Exists:",trinity_out
	else:
		fix = """
sed 's_|_-_g' {} > {}
""".format(trinity_fasta, trinity_out)
    		s = subprocess.Popen(fix, shell=True)
    		print fix
    		s.wait()
	return trinity_out

def transrate(transrate_dir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly):
    #sra = old_assembly.split("_")[-1].split(".")[0]
    sample = "trinity2.2.0_"+mmetsp+"_trinity2014"
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, fixed_fasta, old_assembly)
    commands = [transrate_command]
    process_name = "trans_ref"
    module_name_list = ""
    filename = mmetsp
    print transrate_command
    s = subprocess.Popen(transrate_command, shell=True)
    s.wait()
    #clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)

def transrate_reverse(transrate_dir, mmetsp, fixed_fasta, mmetsp_dir, old_assembly):
    #sra = old_assembly.split("_")[-1].split(".")[0]
    sample = "reverse_trinity2014_" + mmetsp + "_trinity2.2.0"
    transrate_out = transrate_dir + sample + "/" + "assemblies.csv"
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, old_assembly,fixed_fasta)
    print "This is the reverse transrate command:"
    commands = [transrate_command]
    process_name = "trans_ref_reverse"
    module_name_list = ""
    filename = sample
    print transrate_command
    s = subprocess.Popen(transrate_command, shell=True)
    s.wait()
    #clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)


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

def execute(data_frame1,data_frame2,ncgr_dir,trinity_fail, count, basedir):
	assemblydir = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
	old_files = os.listdir(assemblydir)
	id_list = os.listdir(basedir)
        for mmetsp in id_list:
		alt_mmetsp = mmetsp + "_2"
		mmetspdir = basedir + mmetsp + "/"
            	trinitydir = basedir + mmetsp + "/" + "trinity/"
		trinity_files = os.listdir(mmetspdir)
		transrate_dir = mmetspdir + "transrate/"
		clusterfunc.check_dir(transrate_dir)
            	trinity_fasta=trinitydir+"trinity_out_2.2.0.Trinity.fasta"
            	#trinity_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
            	clusterfunc.check_dir(trinitydir)
            	if os.path.isfile(trinity_fasta) == False:
			right = [s for s in trinity_files if s.endswith(".right.fq")][0]
        		left = [s for s in trinity_files if s.endswith(".left.fq")][0]
			right = mmetspdir + right
			left = mmetspdir + left
			if os.path.isfile(left) and os.path.isfile(right):
				#run_trinity(trinitydir,left,right,mmetsp)
                		print "Trinity not finished:", trinity_fasta
                		trinity_fail.append(trinitydir)
            		else:
				print "No files:",left
		else:
                	print "Trinity completed successfully.", trinity_fasta
                	count += 1
                	old_assemblies = glob.glob(assemblydir+"*"+mmetsp+"*")
			if len(old_assemblies) >= 1:
				full_assembly = old_assemblies[0]
			else:
				print glob.glob(assemblydir + "*" + mmetsp + "*")
			#copy_string = "cp " + trinity_fasta + " " + assemblydir
                	#print copy_string
                	#s = subprocess.Popen(copy_string, shell=True)
                	#s.wait()
                	fixed_fasta = fix_fasta(trinity_fasta,trinitydir,mmetsp)
			#sra = old_assembly.split("_")[-1].split(".")[0]
			ncgr_assembly = ncgr_dir + mmetsp + ".nt.fa.fixed.fa"	
			sample = "trinity2.2.0_"+mmetsp+"_trinity2014"
			reverse_sample = "reverse_trinity2014_" + mmetsp + "_trinity2.2.0"
    			transrate_out = transrate_dir + sample + "/" + "assemblies.csv"
			transrate_reverse_assemblies = transrate_dir + reverse_sample + "/" + "assemblies.csv"
			if os.path.isfile(transrate_out):
				print "Transrate completed:",transrate_out
				data1 = parse_transrate_stats(transrate_out,mmetsp,mmetsp)
                                data_frame1 = build_DataFrame(data_frame1,data1)
			else:
				transrate(transrate_dir, mmetsp, fixed_fasta, mmetspdir, full_assembly)
			if os.path.isfile(transrate_reverse_assemblies):
				print "Transrate complete:",transrate_reverse_assemblies
				data2 = parse_transrate_stats(transrate_reverse_assemblies,mmetsp,mmetsp)
                        	data_frame2 = build_DataFrame(data_frame2,data2)
			else:
				transrate_reverse(transrate_dir, mmetsp, fixed_fasta, mmetspdir, full_assembly)
	print "Number of Trinity de novo transcriptome assemblies:"
    	print count
   	print "Number of times Trinity failed:"
    	print len(trinity_fail)
	return data_frame1,data_frame2

basedir = "/mnt/scratch/ljcohen/mmetsp/"
ncgr_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
datafiles = ["SraRunInfo_719.csv"]
data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()
trinity_fail = []
count = 0
data_frame1,data_frame2 = execute(data_frame1,data_frame2,ncgr_dir,trinity_fail, count, basedir)
data_frame1.to_csv("assembly_evaluation_data/trinity2014_trinity2.2.0_transrate_reference.csv")
data_frame2.to_csv("assembly_evaluation_data/trinity2014_trinity2.2.0_transrate_reverse.csv")
