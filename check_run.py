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
    count=0
    url_data={}
    with open(thefile,"rU") as inputfile:
        headerline=next(inputfile).split(',')
        #print headerline        
        position_name=headerline.index("ScientificName")
        position_reads=headerline.index("Run")
        position_ftp=headerline.index("download_path")
        for line in inputfile:
            line_data=line.split(',')
            name="_".join(line_data[position_name].split())
            read_type=line_data[position_reads]
            ftp=line_data[position_ftp]
            name_read_tuple=(name,read_type)
            print name_read_tuple
            #check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                #check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print "url already exists:", ftp
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def download(url,newdir,newfile):
    filestring=newdir+newfile
    urlstring="wget -O "+newdir+newfile+" "+url
    #Note: only for Python 3
    #urllib.request.urlretrieve(url,filestring)
    #Use this for Python 2
    s=subprocess.Popen(urlstring,shell=True)
    s.wait()
    print "Finished downloading from NCBI."


def sra_extract(newdir,newfile):
    #if seqtype=="single":
    #    sra_string="fastq-dump -v "+newdir+file
    #    print sra_string
    #elif seqtype=="paired":
	# check whether .fastq exists in directory
    if glob.glob(newdir+"*.fastq"):
    	print "SRA has already been extracted", newfile
    else:
    	sra_string="fastq-dump -v -O "+newdir+" --split-3 "+newdir+newfile
    	#print sra_string
	print "extracting SRA..."
    	s=subprocess.Popen(sra_string,shell=True,stdout=PIPE)
    	s.wait()
	print "Finished SRA extraction."



def execute(url_data):
	trinity_fail=[]
	empty_files=[]
	for item in url_data.keys():
        	organism=item[0]
        	seqtype=item[1]
        	org_seq_dir=basedir+organism+"/"
		clusterfunc.check_dir(org_seq_dir)
        	url_list=url_data[item]
        	for url in url_list:
            		sra=basename(urlparse(url).path)
            		newdir=org_seq_dir+sra+"/"
			filename=newdir+sra
			## check if trinity exists
			trinitydir=newdir+"trinity/"
			left=trinitydir+"left.fq"
			right=trinitydir+"right.fq"
			if os.stat(left).st_size == 0:
				print "File is empty:",left
				if sra not in empty_files:
					empty_files.append(sra)
			if os.stat(right).st_size == 0:
				print "File is empty:",right
				if sra not in empty_files:
					empty_files.append(sra)
			trinity_outputdir=trinitydir+"trinity_out/"
			trinity_file=trinity_outputdir+"Trinity.fasta"
			if os.path.isfile(trinity_file):
				print "Trinity completed successfully:",trinity_file
			else:
				print "Trinity needs to be run again:",filename
				trinity_fail.append(sra)
			diginormdir=newdir+"diginorm/"
			trimdir=newdir+"trim/"
	print "List of empty files:"
	print empty_files
	print "Trinity needs to be run again:"
	print trinity_fail
	return empty_files, trinity_fail



def run_trimmomatic_TruSeq(trimdir,file1,file2,sra):
  	bash_filename=trimdir+sra+".trim.TruSeq.sh"
    # need a better check for whether this process has been run:
    #if os.path.isfile(bash_filename):
#	print "trim file already written",bash_filename
 #   else:
	j="""#!/bin/bash
java -Xmx10g -jar /bin/Trimmomatic-0.33/trimmomatic-0.33.jar PE \\
-baseout {}.Phred30.TruSeq.fq \\
{} {} \\
ILLUMINACLIP:/bin/Trimmomatic-0.33/adapters/combined.fa:2:40:15 \\
SLIDINGWINDOW:4:2 \\
LEADING:2 \\
TRAILING:2 \\
MINLEN:25 &> trim.{}.log
""".format(sra,file1,file2,sra)
	os.chdir(trimdir)	
	with open(bash_filename,"w") as bash_file:
		bash_file.write(j)
    	print "file written:",bash_filename
    	print "Trimming with Trimmomatic now..."
	s=subprocess.Popen("sudo bash "+bash_filename,shell=True)
    	s.wait()
    	print "Trimmomatic completed."
    	os.chdir("/home/ubuntu/MMETSP/")



def interleave_reads(trimdir,sra,interleavedir):
    	interleavefile=interleavedir+sra+".trimmed.interleaved.fq"
    #if os.path.isfile(interleavefile):
#	print "already interleaved"
 #   else:
    	interleave_string="interleave-reads.py "+trimdir+sra+".Phred30.TruSeq_1P.fq "+trimdir+sra+".Phred30.TruSeq_2P.fq > "+interleavefile
    	print interleave_string
	print "Interleaving now..."
    	s=subprocess.Popen(interleave_string,shell=True)    
    	s.wait()
	print "Reads interleaved."


def make_orphans(trimdir):
    #if os.path.isfile(trimdir+"orphans.fq.gz"):
#	print "orphans file exists:",trimdir+"orphans.fq.gz"
 #   else:
	listoffiles=os.listdir(trimdir)
    	orphanreads=[]
    	for i in listoffiles:
		if i.endswith("_1U.fq"):
			orphanreads.append(trimdir+i)
		elif i.endswith("_2U.fq"):
			orphanreads.append(trimdir+i)
    	# does it matter what order the orphans are added?
	# it seems that 2P is always empty, is that normal?
	orphanlist=" ".join(orphanreads)
    	print orphanlist
    	orphan_string="gzip -9c "+orphanlist+" > "+trimdir+"orphans.fq.gz"
    	print orphan_string
    	s=subprocess.Popen(orphan_string,shell=True)
    	s.wait()


def run_diginorm(diginormdir,interleavedir,trimdir):
	# this will create and run a script from the working directory
	# output *.keep files will be in the working directory
	#if glob.glob(diginormdir+"*keep*"):
	#	print "normalize-by-median.py already run"
	#else:
		j="""
normalize-by-median.py -p -k 20 -C 20 -M 4e9 \\
--savegraph {}norm.C20k20.ct -u \\
{}orphans.fq.gz \\
{}*.fq
""".format(diginormdir,trimdir,interleavedir)
		os.chdir(diginormdir)
		with open("diginorm.sh","w") as diginormfile:
			diginormfile.write(j)
		s=subprocess.Popen("sudo bash diginorm.sh",shell=True)
		s.wait()
		#s=subprocess.Popen("cat diginorm.sh",shell=True)
		#s.wait()
		os.chdir("/home/ubuntu/MMETSP/")



def run_filter_abund(diginormdir):
	#if glob.glob(diginormdir+"*keep.abundfilt*"):
	#	print "filter-abund.py already run"
	#else:
		j="""
filter-abund.py -V -Z 18 {}norm.C20k20.ct {}*.keep
""".format(diginormdir,diginormdir)
		os.chdir(diginormdir)
		with open("filter_abund.sh","w") as abundfile:
			abundfile.write(j)
		s=subprocess.Popen("sudo bash filter_abund.sh",shell=True)
		s.wait()
		os.chdir("/home/ubuntu/MMETSP/")


def rename_files(diginormdir):
	#if glob.glob(diginormdir+"*.abundfilt.pe"):
	#	print "paired reads already extracted"
	#else:
		j="""
for file in *.abundfilt
do
	extract-paired-reads.py ${{file}}
done
""".format()
		os.chdir(diginormdir)
		with open("rename.sh","w") as renamefile:
			renamefile.write(j)
		#s=subprocess.Popen("cat rename.sh",shell=True)
		#s.wait()
		s=subprocess.Popen("sudo bash rename.sh",shell=True)
		s.wait()
		os.chdir("/home/ubuntu/MMETSP/")



def combine_orphaned(diginormdir):
	#if glob.glob(diginormdir+"orphans.keep.abundfilt.fq.gz"):
#		print "orphan reads already combined"
#	else:
		j="""
gzip -9c {}orphans.fq.gz.keep.abundfilt > {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
	gzip -9c ${{file}} >> orphans.keep.abundfilt.fq.gz
done
""".format(diginormdir,diginormdir,diginormdir,diginormdir)
		os.chdir(diginormdir)
		print "combinding orphans now..."
		with open("combine_orphaned.sh","w") as combinedfile:
			combinedfile.write(j)
		#s=subprocess.Popen("cat combine_orphaned.sh",shell=True)
		#s.wait()
		print "Combining *.se orphans now..."
		s=subprocess.Popen("sudo bash combine_orphaned.sh",shell=True)
		s.wait()
		print "Orphans combined."
		os.chdir("/home/ubuntu/MMETSP/")



def rename_pe(diginormdir):
	j="""
for file in {}*trimmed.interleaved.fq.keep.abundfilt.pe
do
	newfile=${{file%%.fq.keep.abundfilt.pe}}.keep.abundfilt.fq
	mv ${{file}} ${{newfile}}
	gzip ${{newfile}}
done
""".format(diginormdir)
	os.chdir(diginormdir)
	with open("rename.sh","w") as renamefile:
		renamefile.write(j)
	#s=subprocess.Popen("cat rename.sh",shell=True)
	#s.wait()
	print "renaming pe files now..."
	s=subprocess.Popen("sudo bash rename.sh",shell=True)	
	s.wait()
	os.chdir("/home/ubuntu/MMETSP/")	


def build_files(trinitydir,diginormfile,SRA):
# takes diginormfile in,splits reads and put into newdir
	buildfiles=trinitydir+SRA+".buildfiles.sh"
	with open(buildfiles,"w") as buildfile:
   		buildfile.write("split-paired-reads.py -d "+trinitydir+" "+diginormfile+"\n")
		buildfile.write("cat "+trinitydir+"*.1 > "+trinitydir+SRA+".left.fq"+"\n")
		buildfile.write("cat "+trinitydir+"*.2 > "+trinitydir+SRA+".right.fq"+"\n")
		# need to fix , orphans are now combined for whole dataset, this is incorrect
		# should be separate orphans file for each sample 
		#buildfile.write("gunzip -c orphans.keep.abundfilt.fq.gz >> left.fq")
	s=subprocess.Popen("sudo bash "+str(buildfiles),shell=True)
	s.wait()

def get_trinity_script(trinitydir,SRA):
	trinityfiles=trinitydir+SRA+".trinityfile.sh"	
	s="""#!/bin/bash
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi
/bin/trinity*/Trinity --left {}{}.left.fq \\
--right {}{}.right.fq --output {}trinity_out --seqType fq --max_memory 14G	\\
--CPU ${{THREADS:-2}}
""".format(trinitydir,trinitydir,trinitydir,trinitydir,trinitydir,SRA,trinitydir,SRA,trinitydir)
	with open(trinityfiles,"w") as trinityfile:	
		trinityfile.write(s)
#string interpolation
#have .format specify dicionary
	#test_string="cat "+trinityfiles
	#s=subprocess.Popen(test_string,shell=True)
	#s.wait()
	return trinityfiles
#make a new run.sh in ~/MMETSP/ to run all *.trinityfile.sh in serial

def run_trinity(trinity_script_list):
	# need to run serially
	# in general, this is a bad idea
	# under normal circumstances, would run in parallel, one process for each Trinity
	# need to loop through and get name of all Trinity scripts
 	# make a script running all scripts
	print trinity_script_list
	runfile="/home/ubuntu/MMETSP/run.sh"
	with open(runfile,"w") as run_file:
		run_file.write("#!/bin/bash"+"\n") 
		for script in trinity_script_list:
			command="sudo bash "+script
			run_file.write(command+"\n")
	print "File written:",runfile
	print "run with:"
	print "sudo bash run.sh"	

def run_empty(empty_files,url_data):
	trinity_scripts=[]
        for SRA in empty_files:
                print SRA
                for item in url_data.keys():
                        organism=item[0]
                        seqtype=item[1]
                        org_seq_dir=basedir+organism+"/"
                        clusterfunc.check_dir(org_seq_dir)
                        url_list=url_data[item]
                        for url in url_list:
                                sra=basename(urlparse(url).path)
                                if sra==SRA:
                                        newdir=org_seq_dir+sra+"/"
                                        clusterfunc.check_dir(newdir)
					newfile=sra
					print newfile
                                        print "Match, should be downloaded:",SRA
					#download(url,newdir,newfile)
					#sra_extract(newdir,newfile)
					trimdir=newdir+"trim/"
					interleavedir=newdir+"interleave/"
					clusterfunc.check_dir(trimdir)
					interleavedir=newdir+"interleave/"
					clusterfunc.check_dir(interleavedir)
					file1=newdir+sra+"_1.fastq"
					file2=newdir+sra+"_2.fastq"
					diginormdir=newdir+"diginorm/"
					clusterfunc.check_dir(diginormdir)
					diginormfile=diginormdir+SRA+".trimmed.interleaved.keep.abundfilt.fq.gz"
					#if os.path.isfile(file1) and os.path.isfile(file2):
					#	print file1
					#	print file2
						#fastqc_report(datadir,fastqcdir)
						### need to fix so the following steps run themselves:
						#run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
						#interleave_reads(trimdir,sra,interleavedir)
                				#run_jellyfish(trimdir,sra)
						#make_orphans(trimdir)
					#else:
					#	print "Files do not exist:",file1,file2 	
					#run_diginorm(diginormdir,interleavedir,trimdir)
                                        #run_filter_abund(diginormdir)
                                        #rename_files(diginormdir)
                                        #combine_orphaned(diginormdir)
                                        #rename_pe(diginormdir)
					trinitydir=newdir+"trinity/"
					clusterfunc.check_dir(trinitydir)
					if os.path.isfile(diginormfile):
				        	print "file exists:",diginormfile
					trinity_script=get_trinity_script(trinitydir,SRA)
					trinity_scripts.append(trinity_script)
					build_files(trinitydir,diginormfile,SRA)
		run_trinity(trinity_scripts)
basedir="/mnt/mmetsp/"
datafile="MMETSP_SRA_Run_Info_subset_b.csv"
url_data=get_data(datafile)
print url_data
empty_files,trinity_fail=execute(url_data)
print empty_files
print trinity_fail
run_empty(empty_files,url_data)
