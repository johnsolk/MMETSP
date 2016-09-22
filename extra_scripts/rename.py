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
        #clusterfunc.qsub_file(diginormdir,process_name,module_name_list,filename,commands)

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
        clusterfunc.qsub_file(trinitydir,process_name,module_name_list,filename,commands)

def check_trinity(seqdir,SRA,count):
   trinity_dir=seqdir+"trinity/"
   trinity_file=trinity_dir+"trinity_out/Trinity.fasta"
   if os.path.isfile(trinity_file)==False:
        if os.path.isdir(trinity_dir)==False:
            print "Still need to run.",trinity_dir
            run_trinity(trinity_dir,SRA)
            count += 1
	else:
            print "Incomplete:",trinity_dir
	    run_trinity(trinity_dir,SRA)
	    count += 1 
   return count

def fix_fasta(trinity_fasta,trinity_dir,sample):
        os.chdir(trinity_dir)
        trinity_out=trinity_dir+sample+".Trinity.fixed.fasta"
        fix="""
sed 's_|_-_g' {} > {}
""".format(trinity_fasta,trinity_out)
        #s=subprocess.Popen(fix,shell=True)
       	print fix
        #s.wait()
        os.chdir("/mnt/home/ljcohen/MMETSP/")
        return trinity_out

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


def execute(trinity_fail,count,basedir,url_data,mmetsp_data):
	different = []
        for item in url_data.keys():
		alt = "blank"
        #Directory will be located according to organism and read type (single or paired)
		organism = item[0].replace("'","")
                seqtype = item[1].replace("'","")
		mmetsp_id = item[2].replace("'","")
		strain,organism_mmetsp,different,alt = get_strain(different,mmetsp_id,organism,mmetsp_data)
		org_seq_dir=basedir+organism+"/"
                # from here, split paired reads
                # then go do assembly
                #clusterfunc.check_dir(org_seq_dir)
                url_list=url_data[item]
                for url in url_list:
                        SRA=basename(urlparse(url).path)
			if alt == "blank":
				sample = organism+"_"+strain+"_"+SRA+"_"+mmetsp_id
                        else:
				sample = organism+"_"+strain+"_"+SRA+"_"+mmetsp_id+"_alt_"+alt
			newdir=org_seq_dir+SRA+"/"
                        diginormdir=newdir+"diginorm/"
                        diginormfile=diginormdir+"qsub_files/"+SRA+".trimmed.interleaved.fq.keep.abundfilt.pe"
                        trinitydir=newdir+"trinity/"
                        #trinity_fasta=trinitydir+"trinity_out/"+"Trinity.fasta"
			# 648 assemblies
			#trinity_fasta=trinitydir+SRA+".Trinity.fasta"
			# 596 assemblies
			# 656 assemblies
			trinity_fasta_new =trinitydir+sample+".Trinity.fixed.fasta"
			trinity_fasta = trinitydir+organism+"_"+SRA+".Trinity.fixed.fasta"
			#clusterfunc.check_dir(trinitydir)
			if os.path.isfile(trinity_fasta) == False:
                        #if os.path.isfile(trinity_fasta):
                                #print "file exists:",trinity_fasta
                                #rename_files(trinitydir,diginormdir,diginormfile,SRA)
                                #run_trinity(trinitydir,SRA)
				#print "Trinity failed:",trinity_fasta
				trinity_fail.append(newdir)
                        else:
                                #print "Trinity completed successfully.",trinity_fasta
				count+=1
				assemblydir="/mnt/scratch/ljcohen/mmetsp_assemblies/"
			#if alt != "blank":
				#print trinity_fasta_new
			#print trinity_fasta
				#copy_string="cp "+trinity_fasta+" "+trinity_fasta_new
				copy_string="cp "+trinity_fasta_new+" "+assemblydir
				print copy_string
				#s=subprocess.Popen(copy_string,shell=True)
        			#s.wait()
				#trinity_out=fix_fasta(trinity_fasta,trinitydir,sample)
				#print "Needs to be fixed:",trinity_fasta
				#print trinity_out
				#"Re-run diginorm:",diginormfile
                        #count = check_trinity(newdir,SRA,count)
			#else:
			#	print "missing Trinity:",trinity_fasta
	print "This is the number of Trinity de novo transcriptome assemblies:"
        print count
        #print "This is the number of times Trinity failed:"
        #print len(trinity_fail)
        #print trinity_fail
        #return trinity_fail,count
	return different

basedir="/mnt/scratch/ljcohen/mmetsp/"
mmetsp_file="/mnt/home/ljcohen/MMETSP/imicrobe/Callum_FINAL_biosample_ids.csv"
datafiles=["SraRunInfo.csv"]
#datafiles=["MMETSP_SRA_Run_Info_subset_msu1.csv","MMETSP_SRA_Run_Info_subset_msu2.csv","MMETSP_SRA_Run_Info_subset_msu3.csv","MMETSP_SRA_Run_Info_subset_msu4.csv",
#        "MMETSP_SRA_Run_Info_subset_msu5.csv","MMETSP_SRA_Run_Info_subset_msu6.csv","MMETSP_SRA_Run_Info_subset_msu7.csv"]
trinity_fail=[]
count=0
for datafile in datafiles:
	url_data=get_data(datafile)
	mmetsp_data=get_mmetsp_data(mmetsp_file)
	#for MMETSP_ID in mmetsp_data:
	#	if len(mmetsp_data[MMETSP_ID]) >= 2:
	#		print MMETSP_ID
	#		print mmetsp_data[MMETSP_ID]
	#print mmetsp_data
	different = execute(trinity_fail,count,basedir,url_data,mmetsp_data)
	print "Differences between MMETSP and SRA organism names:"
	print len(different)
	#for i in different:
	#	print i
#print "Number of Trinity assemblies:"
#print count
#print "Total number of times Trinity failed:"
#print len(trinity_fail)
#print trinity_fail

#for dirname in trinity_fail:
#	SRA=dirname.split("/")[6]
#	genus_species=dirname.split("/")[5]
#	sample=genus_species+"_"+SRA
#	trinitydir=dirname+"trinity/"
#	trinity_out_dir=trinitydir+"trinity_out/"
#	print trinitydir
#	#clusterfunc.check_dir(trinitydir)
#	run_trinity(trinitydir,SRA)
	#trinity_fasta = trinitydir+
#	trinity_fasta = trinity_out_dir+"Trinity.fasta"
#	if os.path.isfile(trinity_fasta):
#		print "file exists:",trinity_fasta
#		new_trinity_fasta=fix_fasta(trinity_fasta,trinitydir,sample)
#		print "New file created:",new_trinity_fasta
#	else:
#		print "Still failed:",trinity_out_dir
