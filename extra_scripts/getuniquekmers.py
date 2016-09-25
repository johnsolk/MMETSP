import os
import os.path
import subprocess
from subprocess import Popen, PIPE
import clusterfunc
from khmer import HLLCounter

def get_unique_kmers(sra,fasta):
	print fasta
	counter = HLLCounter(0.1,25)
	counter.consume_fasta(fasta)
	unique_kmers = counter.estimate_cardinality()
	print unique_kmers
	return unique_kmers

def make_unique_kmers_dictionary(sample_dictionary,fasta,sra):
	unique_kmers = get_unique_kmers(sra,fasta)
	sample_dictionary[sra]=unique_kmers				
    	return sample_dictionary

def make_unique_kmer_table(sample_dictionary,unique_kmers_filename):
    header=["Sample","Unique_kmers"]
    with open(unique_kmers_filename,"w") as datafile:
        datafile.write("\t".join(header))
        datafile.write("\n")
        for sample in sample_dictionary.keys():
            datafile.write(sample+"\t")
	    unique_kmers = str(sample_dictionary[sample])
            datafile.write(unique_kmers)
            datafile.write("\n")
    datafile.close()

def execute(fasta_list,unique_kmers_filename,basedir):
	sample_dictionary = {}
        for fasta in fasta_list:
		if fasta.endswith(".fasta"):
			sample_info = fasta.split("_")
			print sample_info
                	for item in sample_info:
				if item.startswith("SRR"):
                			sra = item
					position = sample_info.index(item)
					mmetsp = sample_info[position+1]
			fasta_full = basedir + fasta
			sample_dictionary = make_unique_kmers_dictionary(sample_dictionary,fasta_full,sra)
	#print sample_dictionary
	make_unique_kmer_table(sample_dictionary,unique_kmers_filename)

basedir = "/Users/cohenl06/Documents/UCDavis/dib/MMETSP/assemblies/mmetsp_assemblies/"
unique_kmers_filename = "/Users/cohenl06/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/unique_kmers.txt"
datafile = "../SraRunInfo.csv"
fasta_list = os.listdir(basedir)
execute(fasta_list,unique_kmers_filename,basedir)
print "File written:",unique_kmers_filename
