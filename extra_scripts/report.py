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
<<<<<<< .merge_file_oAh5J2
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats, integrate
import seaborn as sns
#sns.set(color_codes=True)
=======
#import numpy as np
#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt
#import pandas as pd
#from scipy import stats, integrate
#import seaborn as sns
#sns.set(color_codes=True)


>>>>>>> .merge_file_XBR5x5

def get_data(thefile):
    mmetsp_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
        #print headerline        
        position_name=headerline.index("ScientificName")
        position_reads=headerline.index("Run")
        position_mmetsp=headerline.index("SampleName")
	for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            read_type=line_data[position_reads]
            mmetsp=line_data[position_mmetsp] 
	    test_mmetsp=mmetsp.split("_")
	    if len(test_mmetsp)>1:
		print mmetsp
		print test_mmetsp
		mmetsp=test_mmetsp[0]
            name_read_tuple=(name,read_type)
            #print name_read_tuple
            #check to see if Scientific Name and run exist
            if name_read_tuple in mmetsp_data.keys():
                #check to see if ftp exists
                if mmetsp in mmetsp_data[name_read_tuple]:
                    print "mmetsp ID already exists:", mmetsp
                else:
                    mmetsp_data[name_read_tuple].append(mmetsp)
            else:
                mmetsp_data[name_read_tuple] = [mmetsp]
        return mmetsp_data

def fix_fasta(trinity_fasta,trinity_dir,sample):
	#os.chdir(trinity_dir)
	trinity_out=trinity_dir+sample+".Trinity.fixed.fa"
	fix="""
sed 's_|_-_g' {} > {}
""".format(trinity_fasta,trinity_out)
	#s=subprocess.Popen(fix,shell=True)
	print fix
        #s.wait()
	#os.chdir("/home/ubuntu/MMETSP/")
	return trinity_out


def fix_fasta_reference(mmetsp_assembly,mmetsp_assembly_dir):
        mmetsp_assembly_out=mmetsp_assembly_dir+mmetsp_assembly+".fixed.fa"
        fix="""
sed 's_|_-_g' {}{} > {}
""".format(mmetsp_assembly_dir,mmetsp_assembly,mmetsp_assembly_out)
	print fix
        #s=subprocess.Popen(fix,shell=True)
        #s.wait()
        return mmetsp_assembly_out


def transrate(transrate_dir,sample,trinity_fasta,mmetsp_assemblies_dir,filename):
	transrate_command="""
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 4
""".format(transrate_dir,sample,trinity_fasta,filename)
	print transrate_command
	#s=subprocess.Popen(transrate_command,shell=True)
	#s.wait()


def transrate_reverse(transrate_dir,sample,trinity_fasta,mmetsp_assemblies_dir,filename):
	transrate_command="""
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 4
""".format(transrate_dir,sample,filename,trinity_fasta)
	print "This is the reverse transrate command:"
	print transrate_command
	#s=subprocess.Popen(transrate_command,shell=True)
	#s.wait()


def parse_transrate_stats(transrate_assemblies):
        data=pd.DataFrame.from_csv(transrate_assemblies,header=0,sep=',')
        return data

def build_DataFrame(data_frame,transrate_data):
        #columns=["n_bases","gc","gc_skew","mean_orf_percent"]
	frames=[data_frame,transrate_data]
	data_frame=pd.concat(frames)
	return data_frame

<<<<<<< .merge_file_oAh5J2
def execute(url_data,basedir,mmetsp_assemblies):
=======
def execute(url_data,basedir):
>>>>>>> .merge_file_XBR5x5
	trinity_fail=[]
	count = 0
	# construct an empty pandas dataframe to add on each assembly.csv to
	for item in mmetsp_data.keys():
		#print item
		organism=item[0]
		sample="_".join(item)
		org_seq_dir=basedir+organism+"/"
		mmetsp_list=mmetsp_data[item]
		for mmetsp in mmetsp_list:
			print mmetsp
			assemblyfileslist=os.listdir(mmetsp_assemblies)
			for filename in assemblyfileslist:
				if filename.startswith(mmetsp):
					if filename.endswith(".fixed.fa"):
						print "This is not the one you want."				
					else:
						print "MMETSP assembly found:",filename
						reference_filename=filename
			sra=item[1]
			newdir=org_seq_dir+sra+"/"
<<<<<<< .merge_file_oAh5J2
			trinitydir=newdir+"trinity/trinity_out/"
			dammit_dir=trinitydir+"dammit_dir/"
			transrate_dir="/mnt/comparisons/"
			reverse_transrate_dir="/mnt/comparisons_reverse/"
			clusterfunc.check_dir(transrate_dir)
			clusterfunc.check_dir(dammit_dir)
			clusterfunc.check_dir(reverse_transrate_dir)
			#trinity_fasta=dammit_dir+"Trinity.fasta.dammit.fasta"
			trinity_fasta=trinitydir+"Trinity.fasta"
			if os.path.isfile(trinity_fasta):
				print trinity_fasta
				fixed_trinity=fix_fasta(trinity_fasta,trinitydir,sample)
				fixed_mmetsp_ref=fix_fasta_reference(reference_filename,mmetsp_assemblies)
				#transrate(transrate_dir,fixed_trinity,mmetsp_assemblies,fixed_mmetsp_ref)
				transrate_reverse(reverse_transrate_dir,sample,fixed_trinity,mmetsp_assemblies_dir,fixed_mmetsp_ref)
=======
			trinitydir=newdir+"trinity/"
			#dammit_dir=trinitydir+"dammit_dir/"
			#transrate_dir=newdir+"transrate/"
			#clusterfunc.check_dir(transrate_dir)
			#trinity_fasta=dammit_dir+"Trinity.fasta.dammit.fasta"
			trinity_fasta=trinitydir+"Trinity.fasta"
			#transrate_out=transrate_dir+sample+"/"
			if os.path.isfile(trinity_fasta):
				#transrate(dammit_dir)
		        	#print transrate_out
				count +=1
				#fixed_trinity=fix_fasta(trinity_fasta,trinitydir,sample)
				#transrate(trinitydir,transrate_out,fixed_trinity)
				#transrate_assemblies=transrate_out+"assemblies.csv"
				#data=parse_transrate_stats(transrate_assemblies)
				#data_frame=build_DataFrame(data_frame,data)
>>>>>>> .merge_file_XBR5x5
			else:
				print "Trinity failed:",newdir
				trinity_fail.append(newdir)	
	print "This is the number of Trinity de novo transcriptome assemblies:"
	print count
	print "This is the number of times Trinity failed:"
	print len(trinity_fail)
	print trinity_fail
<<<<<<< .merge_file_oAh5J2

def get_extra_assemblies(extra_dir,data_frame):
	listofassemblies=os.listdir(extra_dir)
	for assembly_fasta in listofassemblies:
                sample_info=assembly_fasta.split("_")
                sra=sample_info[2].split(".")[0]
		sample_info=sample_info[:-1]
		sample_info.append(sra)
		sample="_".join(sample_info)
		print sample
                transrate_out=extra_dir+sample+"/"
                fixed_trinity=fix_fasta(assembly_fasta,extra_dir,sample)
                transrate(extra_dir,transrate_out,fixed_trinity)
                transrate_assemblies=transrate_out+"assemblies.csv"
                data=parse_transrate_stats(transrate_assemblies)
                data_frame=build_DataFrame(data_frame,data)
	return data_frame

=======
	#return data_frame
>>>>>>> .merge_file_XBR5x5

def get_extra_assemblies_transrate(extradir,transrate_dir,mmetsp_assemblies):
	datafile="/home/ubuntu/MMETSP/MMETSP_SRA_Run_Info_subset2.csv"
	mmetsp_data=get_data(datafile)
	print mmetsp_data
	listofassemblies=os.listdir(extra_dir)
	for filename in listofassemblies:
		if filename.endswith("Trinity.dammit.fasta"):
			print filename
			assembly_filename=extra_dir+filename
			file_info=filename.split("_")
			sra_info=file_info[2].split(".")
			sra=sra_info[0]
			organism=file_info[0]+"_"+file_info[1]
			org_sra=(organism,sra)
			sample=organism+"_"+sra+".dammit"
			print sample
			fixed_trinity=fix_fasta(assembly_filename,extra_dir,sample)
			mmetsp_list=mmetsp_data[org_sra]
			mmetsp=mmetsp_list[0]
			assemblyfileslist=os.listdir(mmetsp_assemblies)
			for ref_filename in assemblyfileslist:
                               if ref_filename.startswith(mmetsp):
					if ref_filename.endswith(".fixed.fa"):
                                                print "This is not the one you want."
                                        else:
                                                print "MMETSP assembly found:",ref_filename
                                                fixed_reference=fix_fasta_reference(ref_filename,mmetsp_assemblies)
						reference_filename=fixed_reference
			#transrate(transrate_dir,sample,fixed_trinity,mmetsp_assemblies,reference_filename)
			transrate_reverse(transrate_dir,sample,fixed_trinity,mmetsp_assemblies_dir,reference_filename)			


def get_contigs_data(data_frame,transrate_dir):
	listofdirs=os.listdir(transrate_dir)
	for dirname in listofdirs:
		transrate_dirname=transrate_dir+dirname+"/"
		transrate_dirnames=os.listdir(transrate_dirname)
		for dirname2 in transrate_dirnames:
			if dirname2.endswith(".fixed"):
				transrate_contigs=transrate_dirname+dirname2+"/contigs.csv"
				if os.path.isfile(transrate_contigs):
					print transrate_contigs
					data=parse_transrate_stats(transrate_contigs)
        				data_frame=build_DataFrame(data_frame,data)
        			else:
					print "File missing:",transrate_contigs
	return data_frame


<<<<<<< .merge_file_oAh5J2

def get_assemblies_data(data_frame,transrate_dir):
        listofdirs=os.listdir(transrate_dir)
        for dirname in listofdirs:
                transrate_assemblies=transrate_dir+dirname+"/assemblies.csv"
                print transrate_assemblies
                if os.path.isfile(transrate_assemblies):
                        data=parse_transrate_stats(transrate_assemblies)
                        data_frame=build_DataFrame(data_frame,data)
                else:
                        print "File missing:",transrate_assemblies
        return data_frame


def get_ref_transrate(transrate_dir):
	listdirs=os.listdir(transrate_dir)
	print listdirs
	for dirname in listdirs:
		newdir=transrate_dir+dirname+"/"
		print newdir
		newfile=newdir+"assemblies.csv"
		if os.path.isfile(newfile):
			print "Exists:",newfile
	        else:
			print "Does not exist:",newfile	


# The following dictionary is formatted as
# basedir:datafile
file_locations={"/mnt2/mmetsp/":"MMETSP_SRA_Run_Info_subset_d.csv",
		"/mnt3/mmetsp/":"MMETSP_SRA_Run_Info_subset_a.csv",
		"/mnt4/mmetsp/":"MMETSP_SRA_Run_Info_subset_b.csv"}
#datafile="MMETSP_SRA_Run_Info_subset2.csv"
extra_dir="/mnt2/mmetsp3/"
data_frame_assemblies=pd.DataFrame()
data_frame_contigs=pd.DataFrame()
mmetsp_assemblies_dir="/mnt/MMETSP_assemblies/"
transrate_dir="/mnt/comparisons/"
reverse_transrate_dir="/mnt/comparisons_reverse/"
#for basedir in file_locations.keys():
#	datafile=file_locations[basedir]
#	mmetsp_data=get_data(datafile)
#	print mmetsp_data
#	data_frame=execute(data_frame,mmetsp_data,basedir,extra_dir,mmetsp_assemblies_dir)


#get_extra_assemblies_transrate(extra_dir,transrate_dir,mmetsp_assemblies_dir)

# check if transrate data exists:
#get_ref_transrate(transrate_dir)

# Grab the transrate data after it has completed:
#data_frame_assemblies=get_assemblies_data(data_frame_assemblies,transrate_dir)
#data_frame_contigs=get_contigs_data(data_frame_contigs,transrate_dir)

#print data_frame_contigs

# print the transrate data to files:
#data_frame_assemblies.to_csv("/home/ubuntu/MMETSP/MMETSP_transrate_data.csv")
#if os.path.isfile("/home/ubuntu/MMETSP/MMETSP_transrate_data.csv"):
#	print "File written: /home/ubuntu/MMETSP/MMETSP_transrate_data.csv"
#data_frame_contigs.to_csv("/home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv")
#if os.path.isfile("/home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv"):
#	print "File written: /home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv"


for basedir in file_locations.keys():
       datafile=file_locations[basedir]
       mmetsp_data=get_data(datafile)
       print mmetsp_data
       #execute(mmetsp_data,basedir,mmetsp_assemblies_dir)

#get_extra_assemblies_transrate(extra_dir,reverse_transrate_dir,mmetsp_assemblies_dir)


# check if transrate data exists:
#get_ref_transrate(reverse_transrate_dir)

# Grab the transrate data after it has completed:
#data_frame_assemblies=get_assemblies_data(data_frame_assemblies,reverse_transrate_dir)
#data_frame_contigs=get_contigs_data(data_frame_contigs,reverse_transrate_dir)

#print data_frame_contigs

# print the transrate data to files:
#data_frame_assemblies.to_csv("/home/ubuntu/MMETSP/MMETSP_reverse_transrate_data.csv")
#if os.path.isfile("/home/ubuntu/MMETSP/MMETSP_reverse_transrate_data.csv"):
#       print "File written: /home/ubuntu/MMETSP/MMETSP_reverse_transrate_data.csv"
		        	#print transrate_out
#data_frame_contigs.to_csv("/home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv")
#if os.path.isfile("/home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv"):
#       print "File written: /home/ubuntu/MMETSP/MMETSP_transrate_reference_comparisons.csv"

=======
basedir = "/mnt/scratch/ljcohen/mmetsp/"	
datafile="SraRunInfo.csv"
url_data=get_data(datafile)
#print url_data
execute(url_data,basedir)
#print data_frame
#data_frame.to_csv("MMETSP_transrate_data.csv")
#get_histogram(data_frame)
>>>>>>> .merge_file_XBR5x5
