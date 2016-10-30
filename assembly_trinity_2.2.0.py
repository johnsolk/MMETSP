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


def combine_orphans(diginormdir):
    diginorm_files_dir = diginormdir + "qsub_files/"
    rename_orphans = """
gzip -9c {}orphans.fq.gz.keep.abundfilt > {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
        gzip -9c ${{file}} >> {}orphans.keep.abundfilt.fq.gz
done
""".format(diginorm_files_dir, diginormdir, diginorm_files_dir, diginormdir)
    return rename_orphans


def rename_files(trinitydir, diginormdir, diginormfile, SRA):
    # takes diginormfile in,splits reads and put into newdir
    rename_orphans = combine_orphans(diginormdir)
    split_paired = "split-paired-reads.py -d " + diginormdir + " " + diginormfile
    rename_string1 = "cat " + diginormdir + "*.1 > " + trinitydir + SRA + ".left.fq"
    rename_string2 = "cat " + diginormdir + \
        "*.2 > " + trinitydir + SRA + ".right.fq"
    rename_string3 = "gunzip -c " + diginormdir + \
        "orphans.keep.abundfilt.fq.gz >> " + trinitydir + SRA + ".left.fq"
    commands = [rename_orphans, split_paired,
                rename_string1, rename_string2, rename_string3]
    process_name = "rename"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = SRA
    # clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)


def run_trinity(trinitydir,left,right,mmetsp):
    trinity_command = """
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out_2.2.0.Trinity.fasta ]; then exit 0 ; fi

Trinity --left {} \\
--right {} --output /tmp/{}.trinity_out_2.2.0 --full_cleanup --seqType fq --max_memory 20G --CPU 16

cp /tmp/{}.trinity_out_2.2.0.Trinity.fasta /mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/
rm -rf /tmp/{}.trinity_out_2.2.0*
""".format(trinitydir, left, right, mmetsp, mmetsp,mmetsp)
    commands = [trinity_command]
    process_name = "trinity_2.2.0"
    module_name_list = ["trinity/2.2.0"]
    filename = mmetsp
    clusterfunc.qsub_file(trinitydir, process_name,
                          module_name_list, filename, commands)


def fix_fasta(trinity_fasta, trinity_dir, sample):
    os.chdir(trinity_dir)
    trinity_out = trinity_dir + sample + ".Trinity.fixed.fasta"
    fix = """
sed 's_|_-_g' {} > {}
""".format(trinity_fasta, trinity_out)
    s = subprocess.Popen(fix, shell=True)
    print fix
    s.wait()
    os.chdir("/mnt/home/ljcohen/MMETSP/")
    return trinity_out

def execute(trinity_fail, count, basedir):
	id_list = os.listdir(basedir)
        for mmetsp in id_list:
		if mmetsp != "qsub_files":
			mmetspdir = basedir + mmetsp + "/"
            		trinitydir = basedir + mmetsp + "/" + "trinity/"
			trinity_files = os.listdir(mmetspdir)
            		trinity_fasta=trinitydir+"trinity_out_2.2.0.Trinity.fasta"
            		#trinity_fasta = trinitydir + sample + ".Trinity.fixed.fasta"
            		clusterfunc.check_dir(trinitydir)
            		if os.path.isfile(trinity_fasta) == False:
				if os.path.isfile("/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"+mmetsp+".trinity_out_2.2.0.Trinity.fasta"):
					print "Trinity finished."
					count +=1
				else:
					print mmetspdir
					right = [s for s in trinity_files if s.endswith(".right.fq")][0]
                        		left = [s for s in trinity_files if s.endswith(".left.fq")][0]
                        		right = mmetspdir + right
                        		left = mmetspdir + left
                        		if os.path.isfile(left) and os.path.isfile(right):
						right = [s for s in trinity_files if s.endswith(".right.fq")][0]
                        			left = [s for s in trinity_files if s.endswith(".left.fq")][0]
                        			right = mmetspdir + right
                       	 			left = mmetspdir + left
						run_trinity(trinitydir,left,right,mmetsp)
                				#print "Trinity failed:", trinity_fasta
                				#trinity_fail.append(trinitydir)
            				else:
						print "No files:",left
			else:
                		print "Trinity completed successfully.", trinity_fasta
                		count += 1
                		assemblydir = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
                		copy_string = "cp " + trinity_fasta + " " + assemblydir
                		print copy_string
                		#s = subprocess.Popen(copy_string, shell=True)
                		#s.wait()
                		# trinity_out=fix_fasta(trinity_fasta,trinitydir,sample)
                		# print "Needs to be fixed:",trinity_fasta
                		# print trinity_out
                		#"Re-run diginorm:",diginormfile
            			#count = check_trinity(newdir,SRA,count)
    	print "Number of Trinity de novo transcriptome assemblies:"
    	print count
   	print "Number of times Trinity failed:"
    	print len(trinity_fail)
    	print trinity_fail
    	return trinity_fail, count

basedir = "/mnt/scratch/ljcohen/mmetsp/"

datafiles = ["SraRunInfo_719.csv"]
trinity_fail = []
count = 0
for datafile in datafiles:
    trinity_fail, count = execute(trinity_fail, count, basedir)
print "Number of Trinity assemblies:"
print count
print "Total number of times Trinity failed:"
print len(trinity_fail)
print trinity_fail
