import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3
# run trimmomatic


def run_trimmomatic_TruSeq(missing, trimmed, remaining, trimdir, file1, file2, sra):
        bash_filename=trimdir+sra+".trim.TruSeq.sh"
        clusterfunc_py3.check_dir(trimdir+"qsub_files/")
        listoffile = os.listdir(trimdir+"qsub_files/")
        trim_file = trimdir+"qsub_files/""trim."+sra+".log"
        matching = [s for s in listoffile if "trim."+sra+".log" in s]
        matching_string = "TrimmomaticPE: Completed successfully"
        if os.path.isfile(trim_file):
                with open(trim_file) as f:
                    content = f.readlines()
        if len(matching)!=0:
                trim_complete = [m for m in content if matching_string in m]
                if len(trim_complete)!=0:
                        print("Already trimmed:",matching)
                        trimmed.append(sra)
                else:
                        missing.append(trimdir)
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
                        orphan_string=make_orphans(trimdir,sra)
                        commands = [j,orphan_string]
                        process_name="trim"
                        module_name_list=""
                        filename=sra
                        clusterfunc_py3.qsub_file(trimdir,process_name,module_name_list,filename,commands)
        else:
                remaining.append(trimdir)
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
                orphan_string=make_orphans(trimdir,sra)
                commands = [j,orphan_string]
                process_name="trim"
                module_name_list=""
                filename=sra
                clusterfunc_py3.qsub_file(trimdir,process_name,module_name_list,filename,commands)
        return missing,trimmed,remaining

def make_orphans(trimdir,sra):
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
	print(file1)
	print(file2)
	if os.path.isfile(file1):
		if os.path.isfile(file2):
			mv_string1 = "cp "+file1+" "+trimdir
			mv_string2 = "cp "+file2+" "+trimdir
			# s=subprocess.Popen(mv_string1,shell=True)
        		# s.wait()
			# t=subprocess.Popen(mv_string2,shell=True)
        		# t.wait()
	# if os.path.isfile(trimdir+sra+".trim_1P.fq"):
	#	if os.path.isfile(trimdir+sra+".trim_2P.fq"):
	#		print "Files all here:",os.listdir(trimdir)
	return mv_string1,mv_string2

def run_move_files(trimdir,sra):
        orphan_string=make_orphans(trimdir,sra)
        mv_string1,mv_string2 = move_files(trimdir,sra)
        commands = [orphan_string,mv_string1,mv_string2]
        process_name="move"
        module_name_list=""
        filename=sra
        clusterfunc_py3.qsub_file(trimdir,process_name,module_name_list,filename,commands)	

def check_files(trimdir,sra):
        file1 = trimdir+sra+".trim_1P.fq"
        file2 = trimdir+sra+".trim_2P.fq"
        if os.path.isfile(file1):
                if os.path.isfile(file2):
                        print("Files all here:",os.listdir(trimdir))
                else:
                        print("Still waiting:",trimdir)

def execute(accession,datadir):
    missing = []
    trimmed = []
    remaining = []
    seq_dir=datadir+accession+"/"
    trimdir=seq_dir+"trim/"
    interleavedir=seq_dir+"interleave/"
    clusterfunc_py3.check_dir(trimdir)
    clusterfunc_py3.check_dir(interleavedir)
    file1=seq_dir+accession+"_1.fastq"
    file2=seq_dir+accession+"_2.fastq"
    #run_trimmomatic_TruSeq(missing, trimmed, remaining, trimdir, file1, file2, accession)    
    run_move_files(trimdir,accession)

accessions = "DRR053698, DRR082659, ERR489297, DRR030368, DRR031870, DRR046632, DRR069093, ERR058009, ERR1016675, SRR2086412, SRR3499127, SRR1789336, SRR2016923, ERR1674585, DRR036858"
accessions = accessions.replace(" ","").split(",")
print(accessions)
basedir = "/mnt/scratch/ljcohen/oysterriver/"
clusterfunc_py3.check_dir(basedir)
for accession in accessions:
   execute(accession,basedir)
