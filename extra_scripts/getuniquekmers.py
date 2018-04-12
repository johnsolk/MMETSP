import os
import os.path
import subprocess
from subprocess import Popen, PIPE
import clusterfunc_py3
from khmer import HLLCounter

def get_unique_kmers(mmetsp,fasta):
    print(fasta)
    counter = HLLCounter(0.1,25)
    counter.consume_seqfile(fasta)
    unique_kmers = counter.estimate_cardinality()
    print(unique_kmers)
    return unique_kmers

def make_unique_kmers_dictionary(sample_dictionary,fasta,mmetsp):
    unique_kmers = get_unique_kmers(mmetsp,fasta)
    sample_dictionary[mmetsp]=unique_kmers
    return sample_dictionary

def make_unique_kmer_table(sample_dictionary,unique_kmers_filename):
    header=["Sample","Unique_kmers"]
    with open(unique_kmers_filename,"w") as datafile:
        datafile.write("\t".join(header))
        datafile.write("\n")
        for sample in sample_dictionary:
            datafile.write(sample+"\t")
            unique_kmers = str(sample_dictionary[sample])
            datafile.write(unique_kmers)
            datafile.write("\n")
    datafile.close()

def execute(fasta_list,unique_kmers_filename,basedir):
    sample_dictionary = {}
    for fasta in fasta_list:
        if fasta.endswith(".fixed.fa"):
            mmetsp= fasta.split(".")[0]
            fasta_file = basedir + fasta
            sample_dictionary = make_unique_kmers_dictionary(sample_dictionary,fasta_file,mmetsp)
            make_unique_kmer_table(sample_dictionary,unique_kmers_filename)

#basedir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0_zenodo/"
unique_kmers_filename = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/unique_kmers_ncgr_nt.txt"
#basedir = "/mnt/home/ljcohen/MMETSP_public/unannotated_assemblies_zenodo/"
#basedir = "/mnt/research/ged/lisa/mmetsp/imicrobe/cds/"
basedir = "/mnt/research/ged/lisa/mmetsp/imicrobe/nt/"
#unique_kmers_filename = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/imicrobe_unique_kmers.txt"
fasta_list = os.listdir(basedir)
execute(fasta_list,unique_kmers_filename,basedir)
print("File written:",unique_kmers_filename)
