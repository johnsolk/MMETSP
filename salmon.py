import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
import glob
import string
# custom Lisa module
import clusterfunc_py3


def get_data(thefile):
    count = 0
    mmetsp_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_mmetsp = headerline.index("SampleName")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            mmetsp = line_data[position_mmetsp]
            test_mmetsp = mmetsp.split("_")
            if len(test_mmetsp) > 1:
                mmetsp = test_mmetsp[0]
            name_read_tuple = (name, read_type)
            if mmetsp in mmetsp_data.keys():
                mmetsp_data[mmetsp].append(name_read_tuple)
            else:
                mmetsp_data[mmetsp] = [name_read_tuple]
        return mmetsp_data

def salmon_index(salmondir, salmon_indexdir, sra, trinity_fasta):
    index = salmon_indexdir + sra + "_index"
    salmon_index_string = "salmon index --index " + index + \
        " --transcripts " + trinity_fasta + " --type quasi"
    return index, salmon_index_string


def quant_salmon(salmon_indexdir,salmondir, sra, mmetsp, newdir, trinity_fasta):
    file1 = newdir + "trim/" + sra + ".trim_1P.fq"
    file2 = newdir + "trim/" + sra + ".trim_2P.fq"
    if os.path.isfile(file1):
        print("file exists:", file1)
    else:
        print("missing:", file1)
    if os.path.isfile(file2):
        print("file exists:", file2)
    index, salmon_index_string = salmon_index(salmondir, salmon_indexdir, sra, trinity_fasta)
    
    salmon_string = "salmon quant -i " + index + " --libType IU -1 " + file1 + \
        " -2 " + file2 + " -o " + salmondir + mmetsp + "_" + sra + ".quant --dumpEq --auxDir aux"
    commands = [salmon_index_string, salmon_string]
    
    print(salmon_index_string)
    print(salmon_string)
    process_name = "salmon"
    module_name_list = ""
    filename = sra
    clusterfunc_py3.qsub_file(salmondir, process_name,module_name_list, filename, commands)

def execute(assemblydir,assemblies,salmon_indexdir,salmondir,basedir,url_data,special_flowers):
    for assemblyfile in assemblies:
        fasta_file = assemblydir + assemblyfile
        mmetsp = assemblyfile.split(".")[0]    
        if mmetsp not in special_flowers:
            list_of_genus_species=url_data[mmetsp]
            print(list_of_genus_species)
            for genus_species_combo in list_of_genus_species:
                  sra=genus_species_combo[1]
                  genus_species=genus_species_combo[0]
                  org_seq_dir = basedir + genus_species + "/"
                  newdir=org_seq_dir+sra+"/"
                  output_dir = salmondir + mmetsp + "_" + sra + ".quant"
                  if os.path.isdir(output_dir):
                      output_files = os.listdir(output_dir)
                      matching = [s for s in output_files if s.endswith(".sf")]
                      if len(matching) >= 1:
                          print("Salmon completed:",output_dir)
                      else:
                          quant_salmon(salmon_indexdir,salmondir,sra,mmetsp,newdir,fasta_file)
                  else:                  
                      quant_salmon(salmon_indexdir,salmondir,sra,mmetsp,newdir,fasta_file)

basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
salmondir="/mnt/home/ljcohen/mmetsp_salmon/"
clusterfunc_py3.check_dir(salmondir)
salmon_indexdir = "/mnt/home/ljcohen/mmetsp_salmon_indexdir/"
clusterfunc_py3.check_dir(salmon_indexdir)
assemblydir="/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
assemblies = os.listdir(assemblydir)
datafile = "SraRunInfo_719.csv"
special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
url_data=get_data(datafile)
print(url_data)
execute(assemblydir,assemblies,salmon_indexdir,salmondir,basedir,url_data,special_flowers)

