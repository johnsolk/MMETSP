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


def get_data(thefile):
    count = 0
    url_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_ftp = headerline.index("download_path")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            ftp = line_data[position_ftp]
            name_read_tuple = (name, read_type)
            print name_read_tuple
            # check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                # check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data


def check_empty(empty_files, file, sra):
    if os.stat(file).st_size == 0:
        print "File is empty:", file
        if sra not in empty_files:
            empty_files.append(sra)
    return empty_files


def check_trinity(assemblies,trinity_fail, trinity_file, sra):
    if os.path.isfile(trinity_file):
        print "Trinity completed successfully:", trinity_file
	assemblies.append(sra)
    else:
        print "Trinity needs to be run again:", trinity_file
        trinity_fail.append(sra)
    return trinity_fail,assemblies


def get_no_files(url_data):
    assemblies = []
    trinity_fail = []
    empty_files = []
    no_files = []
    for item in url_data.keys():
        organism = item[0].replace("'","")
        seqtype = item[1]
        org_seq_dir = basedir + organism + "/"
        clusterfunc.check_dir(org_seq_dir)
        url_list = url_data[item]
        for url in url_list:
            sra = basename(urlparse(url).path)
            newdir = org_seq_dir + sra + "/"
            filename = newdir + sra
            # check if trinity exists
            trinitydir = newdir + "trinity/"
            left = trinitydir + sra + ".left.fq"
            right = trinitydir + sra + ".right.fq"
            if os.path.isfile(left):
	    	empty_files = check_empty(empty_files, left, sra)
		if os.path.isfile(right):
			empty_files = check_empty(empty_files, right, sra)
			trinity_outputdir = trinitydir + "trinity_out/"
            		#trinity_file = trinity_outputdir + "Trinity.fasta"
            		trinity_file = trinitydir + organism + "_" + sra + ".Trinity.fixed.fasta"
			trinity_fail,assemblies = check_trinity(assemblies,trinity_fail, trinity_file, sra)
		else:
			print "Missing right:",right
			if sra not in trinity_fail:
				no_files.append(sra)
            else:
		print "Missing left:",left
		if sra not in no_files:
			if sra not in trinity_fail:
				no_files.append(sra)
    print "Empty files:"
    print empty_files
    print len(empty_files)
    print "Trinity needs to be run again:"
    print trinity_fail
    print len(trinity_fail)
    print "Pipeline needs to be run again:"
    print no_files
    print len(no_files)
    print "Assemblies:"
    print len(assemblies)
    return no_files

def download(url, newdir, newfile):
    urlstring = "wget -O " + newdir + newfile + " " + url
    print urlstring
    #	s = subprocess.Popen(urlstring, shell=True)
    #	s.wait()
	
    #print "Finished downloading from NCBI."
    return urlstring

def sra_extract(newdir, filename):
    sra_string = "fastq-dump -v -O " + newdir + " --split-3 " + newdir + filename
    print sra_string
    #print "extracting SRA..."
    #s = subprocess.Popen(sra_string, shell=True)
    #s.wait()
    #print "Finished SRA extraction."
    return sra_string

def send_to_cluster(newdir,command_list,sra,names):
	commands = []
	for string in command_list:
		commands.append(string)
    		process_name = names
    		module_name_list = ""
    		filename = sra
    		clusterfunc.qsub_file(newdir, process_name,
                          module_name_list, filename, commands)

def fastqc(newdir, fastqcdir, filename):
    listoffiles = os.listdir(newdir)
    print listoffiles
    fastq_file_list = []
    for i in listoffiles:
        if i.endswith(".fastq"):
            fastq_file_list.append(newdir + i)
    fastqc_report(fastq_file_list, newdir, fastqcdir, filename)


def fastqc_report(fastq_file_list, newdir, fastqcdir, filename):
    # imports list of files in each directory
    print fastq_file_list
    print fastqcdir + filename
    if glob.glob(fastqcdir + filename + "_*_fastqc.zip"):
        print "fastqc already complete:", filename
    else:
        # creates command to generate fastqc reports from all files in list
        file_string = str(fastq_file_list)
    # print fastq_file_list
        file_string = " ".join(fastq_file_list)
    # print file_string
        fastqc_string = "fastqc -o " + fastqcdir + " " + file_string
    	print "fastqc reports being generated for: " + str(fastq_file_list)
    	fastqc_command = [fastqc_string]
    	process_name = "fastqc"
    	module_name_list = ""
    	filename = filename
    	clusterfunc.qsub_file(fastqcdir, process_name,
                          module_name_list, filename, fastqc_command)


def run_trimmomatic_TruSeq(trimdir, file1, file2, sra):
        bash_filename=trimdir+sra+".trim.TruSeq.sh"
        clusterfunc.check_dir(trimdir+"qsub_files/")
        listoffile = os.listdir(trimdir+"qsub_files/")
        # print listoffile
        trim_file = trimdir+"qsub_files/""trim."+sra+".log"
        # print trim_file
        matching = [s for s in listoffile if "trim."+sra+".log" in s]
        matching_string = "TrimmomaticPE: Completed successfully"
        if os.path.isfile(trim_file):
                with open(trim_file) as f:
                        content = f.readlines()
        if len(matching)!=0:
                trim_complete = [m for m in content if matching_string in m]
                if len(trim_complete)!=0:
                        print "Already trimmed:",matching
                else:
                        j="""
java -jar /mnt/home/ljcohen/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.trim.fq \\
{} {} \\
ILLUMINACLIP: /mnt/home/ljcohen/bin/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
                        orphan_string=make_orphans(trimdir,sra)
                        mv_string1,mv_string2 = move_files(trimdir,sra)
                	commands = [j,orphan_string,mv_string1,mv_string2]
			process_name="trim"
                        module_name_list=""
                        filename=sra
                        clusterfunc.qsub_file(trimdir,process_name,module_name_list,filename,commands)
        else:
                j="""
java -jar /mnt/home/ljcohen/bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.trim.fq \\
{} {} \\
ILLUMINACLIP:/mnt/home/ljcohen/bin/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
                orphan_string = make_orphans(trimdir,sra)
                mv_string1,mv_string2 = move_files(trimdir,sra)
		commands = [j,orphan_string,mv_string1,mv_string2]
                process_name="trim"
                module_name_list=""
                filename=sra
                clusterfunc.qsub_file(trimdir,process_name,module_name_list,filename,commands)

def make_orphans(trimdir,sra):
    # if os.path.isfile(trimdir+"orphans.fq.gz"):
        # if os.stat(trimdir+"orphans.fq.gz").st_size != 0:
        #       print "orphans file exists:",trimdir+"orphans.fq.gz"
        # else:
        #       print "orphans file exists but is empty:",trimdir+"orphans.fq.gz"
    # else:
        file1 = trimdir+"qsub_files/"+sra+".trim_1U.fq"
        file2 = trimdir+"qsub_files/"+sra+".trim_2U.fq"
        orphanlist=file1 + " " + file2
        orphan_string="gzip -9c "+orphanlist+" > "+trimdir+"orphans.fq.gz"
        #print orphan_string
        # s=subprocess.Popen(orphan_string,shell=True)
        # s.wait()
        return orphan_string

def move_files(trimdir,sra):
        tmp_trimdir = trimdir + "qsub_files/"
        file1 = tmp_trimdir+sra+".trim_1P.fq"
        file2 = tmp_trimdir+sra+".trim_2P.fq"
        mv_string1 = "cp "+file1+" "+trimdir
        mv_string2 = "cp "+file2+" "+trimdir
                        # s=subprocess.Popen(mv_string1,shell=True)
                        # s.wait()
                        # t=subprocess.Popen(mv_string2,shell=True)
                        # t.wait()
        # if os.path.isfile(trimdir+sra+".trim_1P.fq"):
        #       if os.path.isfile(trimdir+sra+".trim_2P.fq"):
        #               print "Files all here:",os.listdir(trimdir)
        return mv_string1,mv_string2

def check_sra(url_data,no_files):
	for item in url_data:
                organism = item[0].replace("'","")
                seqtype = item[1]
                org_seq_dir = basedir + organism + "/"
                clusterfunc.check_dir(org_seq_dir)
                url_list = url_data[item]
                for url in url_list:
			command_list = []
                        sra = basename(urlparse(url).path)
                        newdir = org_seq_dir + sra + "/"
			if sra in no_files:
				if os.path.isdir(newdir):
					print "Directory exists:",sra
					if os.path.isfile(sra):
						print "Exists:",sra
					else:
						print "Missing:",newdir
						clusterfunc.check_dir(newdir)
						print url	
						filestring = newdir + sra
    						if os.path.isfile(filestring):
        						print "file exists:", filestring
						else:
							urlstring = download(url,newdir,sra)
							command_list.append(urlstring)
						if glob.glob(newdir + "*.fastq"):
        						print "SRA has already been extracted", filestring
						else:
							sra_string = sra_extract(newdir,sra)
							command_list.append(sra_string)	
						names = "download_extract"
						print command_list
						if len(command_list) >=1:
							send_to_cluster(newdir,command_list,sra,names)
						else:
							print "Pipeline already run."
							fastqcdir = newdir + "fastqc/"
							clusterfunc.check_dir(fastqcdir)
							fastqc(newdir, fastqcdir, sra)
							trimdir=newdir+"trim/"
							interleavedir=newdir+"interleave/"
                					clusterfunc.check_dir(trimdir)
                					clusterfunc.check_dir(interleavedir)
                					file1=newdir+sra+"_1.fastq"
                					file2=newdir+sra+"_2.fastq"
							if os.path.isfile(file1) and os.path.isfile(file2):
                        					print file1
                        					print file2
								run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
							#run_move_files(trimdir,sra)
basedir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "../SraRunInfo.csv"
url_data = get_data(datafile)
print url_data
no_files = get_no_files(url_data)
check_sra(url_data,no_files)
