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

def get_mmetsp_data(mmetsp_file):
    mmetsp_data={}
    with open(mmetsp_file,"rU") as inputfile:
        headerline=next(inputfile).split(',')
        #print headerline        
        position_mmetsp_id = headerline.index("SAMPLE_NAME")
        position_organism = headerline.index("ORGANISM")
        position_strain = headerline.index("STRAIN")
        for line in inputfile:
            line_data=line.split(',')
	    MMETSP_id = line_data[position_mmetsp_id]
            if MMETSP_id.endswith("C"):
                MMETSP_id = MMETSP_id[:-1]
	    test_mmetsp = MMETSP_id.split("_")
            if len(test_mmetsp) > 1:
                MMETSP_id = test_mmetsp[0]		
            name="_".join(line_data[position_organism].split())
            strain = "-".join(line_data[position_strain].split())
            name_id_tuple=(name,strain)
            #print name_id_tuple
            #check to see if Scientific Name and run exist
            mmetsp_data[MMETSP_id] = name_id_tuple
        return mmetsp_data

def get_strain(different,mmetsp_id,organism,mmetsp_data):
        alt = "blank"
        if mmetsp_id in mmetsp_data:
                name_info = mmetsp_data[mmetsp_id]
                #print name_info]
                strain = name_info[1]
                if "'" in strain:
                        strain = strain.replace("'","")
                if "/" in strain:
                        #print strain
                        strain = strain.replace("/","-")
                        #print strain
                if ")" in strain:
                        strain = strain.replace(")","-")
                if "(" in strain:
                        strain = strain.replace("(","-")
                if "=" in strain:
                        strain = strain.replace("=","-")
                if ":" in strain:
                        strain = strain.replace(":","-")
                organism_mmetsp = name_info[0]
                if organism != organism_mmetsp:
                        organism_mmetsp_data = organism_mmetsp.split("_")
                        organism_data = organism.split("_")
                        #print organism_mmetsp_data
                        #print organism_data
                        if len(organism_mmetsp_data) >= 2:
                                if len(organism_data) >= 2:
                                        if organism != "uncultured_eukaryote":
                                                #print organism_data[1][0:3]
                                                #print organism_mmetsp_data[1]
                                                if organism_mmetsp_data[0] != organism_mmetsp_data[1]:
                                                        if "\x8e" in organism_mmetsp_data[1]:
                                                                organism_mmetsp_data[1] = organism_mmetsp_data[1].replace("\x8e","")
                                                        elif organism_mmetsp_data[1].lower().startswith(organism_data[1].lower()) == False:
                                                                #print "Species are different - imicrobe:"+organism_mmetsp+" SRA:"+organism
                                                                different_tuple = (organism_mmetsp,organism)
                                                                different.append(different_tuple)
                                                                alt = organism_mmetsp
                                                        elif organism_mmetsp.startswith(organism[0:3]) == False:
                                                                different_tuple = (organism_mmetsp,organism)
                                                                different.append(different_tuple)
                                                                #print "Different imicrobe: "+organism_mmetsp+" SRA: "+organism
                                                                alt = organism_mmetsp
                return strain,organism_mmetsp,different,alt
        else:
                print mmetsp_id
		print mmetsp_data
		print "MMETSP id not in mmetsp_data:",mmetsp_id
	
def transrate(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, trinity_fasta, filename)
    commands = [transrate_command]
    process_name = "trans_ref_nt"
    module_name_list = ""
    filename = sample
    print transrate_command
    #clusterfunc.qsub_file(transrate_dir,process_name,module_name_list,filename,commands)

def transrate_reverse(transrate_dir, sample, trinity_fasta, mmetsp_assemblies_dir, filename):
    transrate_command = """
transrate -o {}{} \\
--assembly {} \\
--reference {} \\
--threads 8
""".format(transrate_dir, sample, filename,trinity_fasta)
    print "This is the reverse transrate command:"
    commands = [transrate_command]
    process_name = "trans_ref_reverse_nt"
    module_name_list = ""
    filename = sample
    print transrate_command
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

def execute(mmetsp_data, data_frame1, data_frame2, url_data, basedir, mmetsp_assemblies):
    trinity_fail = []
    different = []
    alt = "blank"
    reference_filename = "blank"
    # construct an empty pandas dataframe to add on each assembly.csv to
    for item in url_data.keys():
        #print item
        organism = item[0].replace("'","")
        sample = "_".join(item)
        org_seq_dir = basedir + organism + "/"
        mmetsp_list = url_data[item]
	for mmetsp in mmetsp_list:
            #print mmetsp
            reference_filename = mmetsp_assemblies+mmetsp+".nt.fa.fixed.fa"
	    #reference_filename = mmetsp_assemblies+mmetsp+".cds.fa.fixed.fa"
	    if os.path.isfile(reference_filename):
            	print "MMETSP assembly found:", reference_filename
                sra = item[1]
		
		strain,organism_mmetsp,different,alt = get_strain(different,mmetsp,organism,mmetsp_data)
                if alt == "blank":
                	sample = organism+"_"+strain+"_"+sra+"_"+mmetsp
               	else:
                        sample = organism+"_"+strain+"_"+sra+"_"+mmetsp+"_alt_"+alt
		newdir = org_seq_dir + sra + "/"
                trinitydir = newdir + "trinity/"
                transrate_dir = newdir + "transrate/"
		transrate_reference_dir = newdir + "transrate_dib_v_ncgr_nt/"
                clusterfunc.check_dir(transrate_reference_dir)
                transrate_reverse_dir = newdir + "transrate_ncgr_nt_v_dib/"
                clusterfunc.check_dir(transrate_reverse_dir)
                #trinity_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
                trinity_fasta = trinitydir + organism + "_" + sra + ".Trinity.fixed.fasta"
		print trinity_fasta
		if os.path.isfile(trinity_fasta) == False:
                    print "Trinity failed:", newdir
                    trinity_fail.append(newdir)
		else:
		    transrate_assemblies_ref = transrate_reference_dir + sample + "/assemblies.csv"
                    transrate_reverse_assemblies = transrate_reverse_dir + sample + "/assemblies.csv"
                    #if os.path.isfile(transrate_assemblies_ref):
		#	       #check_delete_files(transrate_assemblies_ref)
                #                data1 = parse_transrate_stats(transrate_assemblies_ref,sra,mmetsp)
                #                data_frame1 = build_DataFrame(data_frame1, data1)
                #    else:
                #                print "Failed."
                    transrate(transrate_reference_dir, sample, trinity_fasta, mmetsp_assemblies_dir, reference_filename)                                   
                    #if os.path.isfile(transrate_reverse_assemblies):
		    		#check_delete_files(transrate_reverse_assemblies)                
	            #   		data2 = parse_transrate_stats(transrate_reverse_assemblies,sra,mmetsp)
                    #            data_frame2 = build_DataFrame(data_frame2, data2)
                    #else:
                    #            print "Reverse failed."
                    transrate_reverse(transrate_reverse_dir, sample, trinity_fasta, mmetsp_assemblies_dir, reference_filename)   
	    else:
                print "Missing:",reference_filename
		MMETSP_url = mmetsp[:-1]
		ref_url = "ftp://ftp.imicrobe.us/projects/104/transcriptomes/"+MMETSP_url+"/"+mmetsp+".nt.fa.gz"
		get_url_command = "wget -O "+mmetsp_assemblies+mmetsp+".nt.fa.gz"+" "+ref_url
		#print get_url_command 
		#s = subprocess.Popen(get_url_command, shell=True, stdout=PIPE)
        	#s.wait()
		#unzip_command = "gunzip "+mmetsp_assemblies+mmetsp+".nt.fa.gz"
		#print unzip_command
		#t = subprocess.Popen(unzip_command, shell=True, stdout=PIPE)
		#t.wait()
		#fix_command = "sed 's_|_-_g' "+mmetsp_assemblies+mmetsp+".nt.fa > "+mmetsp_assemblies+mmetsp+".nt.fa.fixed.fa"
		#print fix_command
		#u = subprocess.Popen(fix_command, shell=True, stdout=PIPE)
                #u.wait()
		
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



def delete_files(filename):
	os.remove(filename)
	print "File removed:",filename

def check_delete_files(filename):
	if os.path.isfile(filename):
		delete_files(filename)

basedir = "/mnt/scratch/ljcohen/mmetsp/"

mmetsp_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
#mmetsp_assemblies_dir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"

datafiles = ["SraRunInfo.csv"]
mmetsp_file="/mnt/home/ljcohen/MMETSP/imicrobe/Callum_FINAL_biosample_ids.csv"
mmetsp_data=get_mmetsp_data(mmetsp_file)

data_frame1 = pd.DataFrame()
data_frame2 = pd.DataFrame()

for datafile in datafiles:
    url_data = get_data(datafile)
    print url_data
    data_frame1, data_frame2 = execute(
        mmetsp_data, data_frame1, data_frame2, url_data, basedir, mmetsp_assemblies_dir)
#data_frame1.to_csv("assembly_evaluation_data/transrate_reference_scores_nt.csv")
#data_frame2.to_csv("assembly_evaluation_data/transrate_reverse_scores_nt.csv")
#print "Reference scores written: transrate_reference_scores_nt.csv"
#print "Reverse reference scores written: transrate_reverse_scores_nt.csv"
