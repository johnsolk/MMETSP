import os
import os.path
from os.path import basename
from urlparse import urlparse
import clusterfunc
import glob

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

def get_sample_dictionary(sample_dictionary,trim_out_file,sra):
    with open(trim_out_file) as outfile:
		for line in outfile:
			line_split=line.split()
			if line_split[0].startswith("Input"):
				num_reads_input=line_split[3]
				print num_reads_input
				num_reads_surviving=line_split[6]
				print num_reads_surviving
				perc_reads_surviving=line_split[7][1:-2]
				print perc_reads_surviving
				sample_dictionary[sra]=[num_reads_input,num_reads_surviving,perc_reads_surviving]				
    return sample_dictionary

def trim_table(sample_dictionary):
    trim_table_filename="/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/"+"trimmomatic_reads_table.txt"
    header=["Sample","Input Reads","Surviving Reads","Percent Surviving"]
    with open(trim_table_filename,"w") as datafile:
        datafile.write("\t".join(header))
        datafile.write("\n")
        for sample in sample_dictionary.keys():
            important_nums=sample_dictionary[sample]
            datafile.write(sample+"\t")
            datafile.write("\t".join(important_nums))
            datafile.write("\n")
    datafile.close()
    print "Trimmomatic stats written:",trim_table_filename

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
    		#clusterfunc.qsub_file(newdir, process_name,
                #          module_name_list, filename, commands)

def execute(url_data):
	sample_dictionary = {}
	missing = []
	trimmed = []
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
			trimdir = newdir + "trim/qsub_files/"
			listoffile = os.listdir(trimdir)
			#print listoffile
			trim_file = trimdir+"trim."+sra+".log"
        		#print trim_file
        		matching = [s for s in listoffile if "trim."+sra+".log" in s]
        		matching_string = "TrimmomaticPE: Completed successfully"
        		if os.path.isfile(trim_file):
                		with open(trim_file) as f:
                        		content = f.readlines()
        		if len(matching)!=0:
                		trim_complete = [m for m in content if matching_string in m]
                		if len(trim_complete)!=0:
                        		print "Already trimmed:",matching
					sample_dictionary=get_sample_dictionary(sample_dictionary,trim_file,sra)
                			trimmed.append(sra)
				else:
                        		missing.append(trimdir)
					print "Missing:",trimdir
	#print sample_dictionary
	trim_table(sample_dictionary)
	print "Missing trimmed:",len(missing)
	print missing
	print "Trimmed:",len(trimmed)
	print "Out of"
	print len(url_data.keys())
	return missing

def check_sra(url_data,missing):
	num_download = []
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
			trimdir = newdir + "trim/qsub_files/"
			if trimdir in missing:
				if os.path.isdir(newdir):
					print "Directory exists:",sra
					if os.path.isfile(sra):
						print "Exists:",sra
					else:
						num_download.append(newdir)
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
	print "Num to download:",len(num_download)
	print num_download

basedir = "/mnt/scratch/ljcohen/mmetsp/"
datafile = "../SraRunInfo.csv"
url_data = get_data(datafile)
print url_data
missing = execute(url_data)
#check_sra(url_data,missing)	
