import os
import subprocess
from subprocess import Popen, PIPE
# Lisa's custom cluster control module
import clusterfunc

# get OrthoFinder commands
# start with ~40,000 comamnds
# split into 25,000 + extra
# run on 18 nodes

def run_first_OrthoFinder(filesdir):
        first_OrthoFinder_command="""
python /mnt/home/ljcohen/bin/OrthoFinder-master/orthofinder.py -f {} -p
""".format(filesdir)
        print "Run this first:",first_OrthoFinder_command

# fixes fasta files, output Results_date
# with the working directory
# there is a species list
# and SpeciesIDs.txt is conversion file
# it will also makes blastdb files
# those have to be moved or deleted:
	print "after running, run this command to delete BlastDB files:"
	print "You won't need those."
	#print "rm -rf "+workingdir+"BlastDBSpecies*"	
	print "Don't forget to run these commands:"
	print "module load GNU/4.4.5"
	print "module load diamond/0.7.9"

def get_working_dir_name(filesdir,todaysdate):
	workingdir=filesdir+"Results_"+todaysdate+"/WorkingDirectory/"
	return workingdir

def run_OrthoFinder(workingdir,threads):
	final_OrthoFinder_command="""
python /mnt/home/ljcohen/bin/OrthoFinder-master/orthofinder.py -b {} -t {}
""".format(workingdir,threads)
	print final_OrthoFinder_command
        working_dir=os.getcwd()
        os.chdir(workingdir)
        #s=subprocess.Popen(diamond_db_command,shell=True)
        #s.wait()
        os.chdir(working_dir)	


def run_diamond_db(working_dir,new_diamond_dir,species_filename):
	species_name=os.path.splitext(species_filename)[0]
	diamond_db_command="""
diamond makedb --in {}{} -d {}{}
""".format(working_dir,species_filename,new_diamond_dir,species_name)
# this will take in a speciesx.fa
# and output a speciesx.dmnd file
	print diamond_db_command
	working_dir=os.getcwd()
	os.chdir(new_diamond_dir)
	#s=subprocess.Popen(diamond_db_command,shell=True)
	#s.wait()
	os.chdir(working_dir)	

# run diamond blast for each comparison

def run_diamond_loop(diamond_dir,workingdir,new_diamond_dir,species_filename,db_filename):
	fnum_dbnum=species_filename+"_"+db_filename
	output_filename=new_diamond_dir+fnum_dbnum
	if os.path.isfile(output_filename):
		print "diamond already run",output_filename
		return
	else:
		diamond_loop_command="""
diamond blastp -d {}{} -q {}{} -p 27 -a {}
""".format(diamond_dir,db_filename,workingdir,species_filename,output_filename)
		#print diamond_loop_command
		return diamond_loop_command

# convert diamond blast output .daa files into tab-separated txt files for OrthoFinder

def run_diamond_view(diamond_out_dir,workingdir):
	listoffiles = os.listdir(diamond_out_dir)
	species_matches_dir = workingdir+"species_matches/"
	split_num = 4000
	i = 0
	count = 0
	process_string = []
	for filename in listoffiles:
		if filename != "qsub_files":
			if i in range(split_num):
				x_y_info = filename.split("_")
                        	x_info = x_y_info[0].split(".")
                        	x = x_info[0].split("Species")[1]
                        	y_info = x_y_info[1].split(".")
                        	y = y_info[0].split("Species")[1]
                        	x_y = x+"_"+y
                        	output_filename = species_matches_dir+"Blast"+x_y+".txt"
                        	diamond_view_command="""
diamond view -a {}{} -o {}
""".format(diamond_out_dir,filename,output_filename)
                                process_string.append(diamond_view_command)
                                i+=1
                        else:
                                i = 0
                                basedir = species_matches_dir
                                process_name="diamond_view"
                                module_name_list=["GNU/4.4.5","diamond/0.7.9"]
                                filename="Group_"+str(count)
                                #clusterfunc.qsub_file(basedir,process_name,module_name_list,filename,process_string)
                                process_string=[]
                                count+=1



def get_num_files(filesdir,workingdir):
	listoffiles=os.listdir(workingdir)
	diamond_dir=workingdir+"diamond/"
	clusterfunc.check_dir(diamond_dir)
	species_filenames=[]
	for filename in listoffiles:
        	if filename.startswith("Species"):
                	if filename.endswith(".fa"):
                                species_filenames.append(filename)
	print species_filenames
	species_num = len(species_filenames)
	print "This is the num of species:",species_num
	split_num = 4000
	print split_num
	i = 0
	count = 0
	#block_list = [species_filenames[x:x+split_num] for x in range(0,len(species_filenames),split_num)]
	process_string=[]
	db_files = os.listdir(diamond_dir)
	print len(db_files)
	db_out_dir = workingdir+"diamond_out/"
	clusterfunc.check_dir(db_out_dir)
	for species_filename in species_filenames:
		print species_filename
		for db in db_files:
			if db.endswith(".dmnd"):
				# not necessary to compare species to themselves
				if i in range(split_num):
					#print i
					#db_filename=os.path.splitext(species_filename)[0]
					db_filename=db
					ortho_command=run_diamond_loop(diamond_dir,workingdir,db_out_dir,species_filename,db_filename)
        				process_string.append(ortho_command)
					i+=1
				else:
					i = 0
					basedir=db_out_dir
					process_name="OrthoFinder"
                			module_name_list=["GNU/4.4.5","diamond/0.7.9"]
                			filename="Group_"+str(count)
                			#clusterfunc.qsub_file(basedir,process_name,module_name_list,filename,process_string)
					process_string=[]
                			count+=1

# make diamond database directory "diamond/"
# make "diamond_out/" for output
# run diamond with shell script
# take out -k 500
# -a output filename and will append .daa

def check_failed(failed_file,filesdir,workingdir):
	diamond_dir = filesdir + "Results_Jun25/diamond/"
	diamond_out_dir = filesdir + "Results_Jun25/diamond_out/"
	db_files = os.listdir(diamond_dir)
	split_num = 4000
	i = 0
	count = 0
	process_string = []
	with open(failed_file,"rU") as failed_file_lines:
		for num in failed_file_lines:
			x_y_info = num.split("_")
                        x_info = x_y_info[0].split("Blast")
                        x = x_info[1]
                        y_info = x_y_info[1].split(".")
                        y = y_info[0]
                        species_file  = "Species"+x+".fa"
			db_filename = "Species"+y+".dmnd"
			if os.path.isfile(workingdir+species_file):
				if os.path.isfile(diamond_dir+db_filename):
					if i in range(split_num):
                        			ortho_command = run_diamond_loop(diamond_dir,workingdir,diamond_out_dir,species_file,db_filename)
                        			process_string.append(ortho_command)
                        			i+=1
                			else:
                        			i = 0
                        			basedir = diamond_out_dir
                        			process_name = "OrthoFinder"
                        			module_name_list = ["GNU/4.4.5","diamond/0.7.9"]
                        			filename = "Group_"+str(count)
                        			clusterfunc.qsub_file(basedir,process_name,module_name_list,filename,process_string)
                        			process_string=[]
                        			count+=1
				else:
					print "db_filename doesn't exist:",db_filename
			else:
				print "species_filename doesn't exist:",species_file
			


def execute(filesdir,threads,todaysdate):
	#run_first_OrthoFinder(filesdir)
	workingdir=get_working_dir_name(filesdir,todaysdate)
	print workingdir
	#diamond_dir=workingdir+"diamond/"
	#clusterfunc.check_dir(diamond_dir)
	#diamond_out_dir = workingdir + "diamond_out/"
	#species_files=os.listdir(workingdir)
	#get_num_files(filesdir,workingdir)
	#run_diamond_view(diamond_out_dir,workingdir)
	#run_OrthoFinder(workingdir,threads)
	failed_file = "NeedToBeRun.txt"
	check_failed(failed_file,filesdir,workingdir)
	
# in this format "Jun24"
todaysdate="Jun25"
threads="27"
filesdir="/mnt/scratch/ljcohen/pep/"
#filesdir="/mnt/scratch/ljcohen/pep_tmp/"
execute(filesdir,threads,todaysdate)
