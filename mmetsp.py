# Lisa J. Cohen
# Lab for Data Intensive Biology, UC Davis
# PI: C. Titus Brown
# transcriptome assembly pipeline
# Marine Microbial Eukaryotic Transcriptome Sequencing Project
# data from Keeling et al. 2014
# http://dx.doi.org/10.1371/journal.pbio.1001889


#1. Get data from spreadsheet

def get_data(thefile):
	"""
	Get data from SRA spreadsheet
	"""
	count=0
    	url_data={}
    	with open(thefile,"rU") as inputfile:
        	headerline=next(inputfile).split(',')
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
