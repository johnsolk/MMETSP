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
        position_MMETSP=headerline.index("SampleName")
        for line in inputfile:
            line_data=line.split(',')
            MMETSP_id = line_data[position_MMETSP]
            name="_".join(line_data[position_name].split())
            read_type=line_data[position_reads]
            ftp=line_data[position_ftp]
            name_read_tuple=(name,read_type,MMETSP_id)
            #print name_read_tuple
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


def check_empty(empty_files, file, sra):
    if os.stat(file).st_size == 0:
        print "File is empty:", file
        if sra not in empty_files:
            empty_files.append(sra)
    return empty_files


def check_trinity(assemblies,trinity_fail, trinity_file, sra):
    if os.path.isfile(trinity_file):
        print "Trinity completed successfully:", trinity_file
	assemblydir = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
        #copy_string="cp "+trinity_fixed_fasta+" "+trinity_fasta_new
        #copy_string="cp "+trinity_fasta_new+" "+assemblydir
        #print copy_string	
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
    return trinity_fail,assemblies

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
                        #clusterfunc.qsub_file(trimdir,process_name,module_name_list,filename,commands)
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
                #clusterfunc.qsub_file(trimdir,process_name,module_name_list,filename,commands)

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

def interleave_reads(trimdir, sra, interleavedir):
    interleavefile = interleavedir + sra + ".trimmed.interleaved.fq"
    if os.path.isfile(interleavefile):
        print "already interleaved"
    else:
        interleave_string = "interleave-reads.py " + trimdir + sra + \
            ".trim_1P.fq " + trimdir + sra + ".trim_2P.fq > " + interleavefile
        print interleave_string
        interleave_command = [interleave_string]
        process_name = "interleave"
        module_name_list = ["GNU/4.8.3", "khmer/2.0"]
        filename = sra
        clusterfunc.qsub_file(interleavedir, process_name,
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
    clusterfunc.qsub_file(diginormdir, process_name,
                          module_name_list, filename, normalize_median_command)

def run_filter_abund(diginormdir, sra):
    keep_dir = diginormdir + "qsub_files/"
    filter_string = """
filter-abund.py -V -Z 18 {}norm.C20k20.ct {}*.keep
""".format(diginormdir, keep_dir)
    extract_paired_string = extract_paired()
    commands = [filter_string, extract_paired_string]
    process_name = "filtabund"
    module_name_list = ["GNU/4.8.3", "khmer/2.0"]
    filename = sra
    clusterfunc.qsub_file(diginormdir, process_name,
                          module_name_list, filename, commands)

def extract_paired():
    extract_paired_string = """
for file in *.abundfilt
do
        extract-paired-reads.py ${{file}}
done
""".format()
    return extract_paired_string

def combine_orphans(diginormdir):
        diginorm_files_dir = diginormdir + "qsub_files/"
        rename_orphans="""
gzip -9c {}orphans.fq.gz.keep.abundfilt > {}orphans.keep.abundfilt.fq.gz
for file in {}*.se
do
        gzip -9c ${{file}} >> {}orphans.keep.abundfilt.fq.gz
done
""".format(diginorm_files_dir,diginormdir,diginorm_files_dir,diginormdir)
        return rename_orphans

def rename_files(trinitydir,diginormdir,diginormfile,SRA):
# takes diginormfile in,splits reads and put into newdir
        rename_orphans = combine_orphans(diginormdir)
        split_paired = "split-paired-reads.py -d "+diginormdir+" "+diginormfile
        rename_string1 = "cat "+diginormdir+"*.1 > "+trinitydir+SRA+".left.fq"
        rename_string2 = "cat "+diginormdir+"*.2 > "+trinitydir+SRA+".right.fq"
        rename_string3 = "gunzip -c "+diginormdir+"orphans.keep.abundfilt.fq.gz >> "+trinitydir+SRA+".left.fq"
        commands=[rename_orphans,split_paired,rename_string1,rename_string2,rename_string3]
        process_name="rename"
        module_name_list=["GNU/4.8.3","khmer/2.0"]
        filename=SRA
        clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)

def run_trinity(trinitydir,SRA):
        trinity_command="""
set -x
# stops execution if there is an error
set -e
if [ -f {}trinity_out/Trinity.fasta ]; then exit 0 ; fi
#if [ -d {}trinity_out ]; then mv {}trinity_out_dir {}trinity_out_dir0 || true ; fi

Trinity --left {}{}.left.fq \\
--right {}{}.right.fq --output {}trinity_out --seqType fq --JM 20G --CPU 16

""".format(trinitydir,trinitydir,trinitydir,trinitydir,trinitydir,SRA,trinitydir,SRA,trinitydir)
        commands=[trinity_command]
        process_name="trinity"
        module_name_list=["trinity/20140413p1"]
        filename=SRA
        #clusterfunc.qsub_file(trinitydir,process_name,module_name_list,filename,commands)


def fix_fasta(trinity_fasta,trinity_dir,sample):
        os.chdir(trinity_dir)
        trinity_out=trinity_dir+sample+".Trinity.fixed.fasta"
        fix="""
sed 's_|_-_g' {} > {}
""".format(trinity_fasta,trinity_out)
        #s=subprocess.Popen(fix,shell=True)
        #print fix
        #s.wait()
        os.chdir("/mnt/home/ljcohen/MMETSP/")
        return trinity_out

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
                print "MMETSP id not in mmetsp_data:",mmetsp_id

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
            name="_".join(line_data[position_organism].split())
            strain = "-".join(line_data[position_strain].split())
            name_id_tuple=(name,strain)
            #print name_id_tuple
            #check to see if Scientific Name and run exist
            mmetsp_data[MMETSP_id] = name_id_tuple
        return mmetsp_data


def check_sra(url_data,no_files,mmetsp_data):
	different = []
	for item in url_data:
		organism = item[0].replace("'","")
                seqtype = item[1]
                mmetsp_id = item[2].replace("'","")
		strain,organism_mmetsp,different,alt = get_strain(different,mmetsp_id,organism,mmetsp_data)
		org_seq_dir = basedir + organism + "/"
                clusterfunc.check_dir(org_seq_dir)
                url_list = url_data[item]
                for url in url_list:
			command_list = []
                        sra = basename(urlparse(url).path)
			if alt == "blank":
                                sample = organism+"_"+strain+"_"+sra+"_"+mmetsp_id
                        else:
                                sample = organism+"_"+strain+"_"+sra+"_"+mmetsp_id+"_alt_"+alt
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
							diginormdir = newdir+"diginormdir/"
							clusterfunc.check_dir(diginormdir)
							trinitydir = newdir + "trinity/"
							clusterfunc.check_dir(trinitydir)
							diginormfile=diginormdir+"qsub_files/"+sra+".trimmed.interleaved.fq.keep.abundfilt.pe"
                					trinity_fasta = trinitydir+"trinity_out/"+"Trinity.fasta"
							#trinity_fasta_new =trinitydir+sample+".Trinity.fixed.fasta"
							trinity_fasta_new = trinitydir + organism + "_" + sra + ".Trinity.fixed.fasta"
							file1=newdir+sra+"_1.fastq"
                					file2=newdir+sra+"_2.fastq"
							assemblydir = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
							if os.path.isfile(file1) and os.path.isfile(file2):
                        					print file1
                        					print file2
								run_trimmomatic_TruSeq(trimdir,file1,file2,sra)
							file1_trim = trimdir+sra+".trim_1P.fq"
        						file2_trim = trimdir+sra+".trim_2P.fq"
							if os.path.isfile(file1_trim) and os.path.isfile(file2):
								#interleave_reads(trimdir, sra, interleavedir)
								#run_diginorm(diginormdir,interleavedir,trimdir,sra)
								#run_filter_abund(diginormdir,interleavedir,trimdir,sra)
								#rename_files(trinitydir,diginormdir,diginormfile,sra)
								if os.path.isfile(trinity_fasta) == False:
									run_trinity(trinitydir,sra)
								else:
									print "Trinity completed!",trinity_fasta
									trinity_fixed_fasta = fix_fasta(trinity_fasta,trinitydir,sra)
									#copy_string="cp "+trinity_fixed_fasta+" "+trinity_fasta_new
                                					copy_string="cp "+trinity_fasta_new+" "+assemblydir
                                					print copy_string
                                					#s=subprocess.Popen(copy_string,shell=True)
                                					#s.wait()


def check_assemblies(url_data,assemblies,mmetsp_data):
        different = []
        for item in url_data:
                organism = item[0].replace("'","")
                seqtype = item[1]
                mmetsp_id = item[2].replace("'","")
                strain,organism_mmetsp,different,alt = get_strain(different,mmetsp_id,organism,mmetsp_data)
                org_seq_dir = basedir + organism + "/"
                clusterfunc.check_dir(org_seq_dir)
                url_list = url_data[item]
                for url in url_list:
                        command_list = []
                        sra = basename(urlparse(url).path)
                        if alt == "blank":
                                sample = organism+"_"+strain+"_"+sra+"_"+mmetsp_id
                        else:
                                sample = organism+"_"+strain+"_"+sra+"_"+mmetsp_id+"_alt_"+alt
                        newdir = org_seq_dir + sra + "/"
                        if sra in assemblies:
                        	trinitydir = newdir + "trinity/"
                                #trinity_fasta = trinitydir+"trinity_out/"+"Trinity.fasta"
                                trinity_fasta_new =trinitydir+sample+".Trinity.fixed.fasta"
				#trinity_fixed_fasta = fix_fasta(trinity_fasta,trinitydir,sra)
                                trinity_fasta_old = trinitydir + organism + "_" + sra + ".Trinity.fixed.fasta"
                                assemblydir = "/mnt/scratch/ljcohen/mmetsp_assemblies/"
                                if os.path.isfile(trinity_fasta_old) == True:
                                        #trinity_fixed_fasta = fix_fasta(trinity_fasta,trinitydir,sra)
                                        #copy_string="cp "+trinity_fasta_old+" "+trinity_fasta_new
                                        copy_string="cp "+trinity_fasta_new+" "+assemblydir
                                        print copy_string
                                        #s=subprocess.Popen(copy_string,shell=True)
                                        #s.wait()
				else:
					print "Trinity finished but don't have fixed version to copy."

basedir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "../SraRunInfo.csv"
mmetsp_file="/mnt/home/ljcohen/MMETSP/imicrobe/Callum_FINAL_biosample_ids.csv"
mmetsp_data=get_mmetsp_data(mmetsp_file)
url_data = get_data(datafile)
print url_data
no_files,assemblies = get_no_files(url_data)
check_sra(url_data,no_files,mmetsp_data)
print len(assemblies)
check_assemblies(url_data,assemblies,mmetsp_data)
rename_string = "for file in /mnt/scratch/ljcohen/mmetsp_assemblies/*; do mv $file ${file/.fixed.fasta/.fasta}; done"
#s=subprocess.Popen(rename_string,shell=True)
#s.wait()
