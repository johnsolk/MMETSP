import pandas as pd
import os
from dammit.fileio.gff3 import GFF3Parser
import glob

def get_dammit_ids(mmetsp,namemap_file,annotations_dir):
    names = pd.read_csv(namemap_file)
    # should be something like: "TRINITY_DN1286_c0_g1_i1 len=850 path=[1655:0-849] [-1, 1655, -2]"
    # parse so only TRINITY_DN1286_c0_g1_i1
    temp_dataframe = pd.DataFrame()
    for i,row in names.iterrows(): 
        trinity_id_long = row['original']
        trinity_id = trinity_id_long.split()[0]
        renamed = row['renamed']
        temp_dataframe = temp_dataframe.append({'seqid': str(trinity_id),'renamed':str(renamed)},ignore_index =True)
    new_out = annotations_dir + mmetsp + ".renamed.csv"
    temp_dataframe.to_csv(new_out)
    return names
               

def get_salmon_quant(salmon_quant_file):
    salmon_data = pd.DataFrame.from_csv(quant_file, sep='\t',index_col = "Name")
    numreads = salmon_data['TPM']
    return data

def execute(dammit_dirs,dammit_dir,salmon_dir,annotations_dir):
    for dirname in dammit_dirs:
        if dirname.endswith("fasta.dammit"):
            print(dirname)
            mmetsp = dirname.split(".")[0]
            namemap_file = dammit_dir + dirname + "/" + mmetsp + ".trinity_out_2.2.0.Trinity.fasta.dammit.namemap.csv"
            if os.path.isfile(namemap_file):
               print(namemap_file)
               names = get_dammit_ids(mmetsp,namemap_file,annotations_dir)
            else:
               print("Does not exist:",namemap_file)
            #salmon_quant_dir = salmon_dir + mmetsp + "*.quant"
            #if len(glob.glob(salmon_quant_dir)) == 1:
             #   salmon_dirname = glob.glob(salmon_quant_dir)[0]
              #  salmon_quant_file = salmon_dirname + "quant.sf"
               # if os.path.isfile(salmon_quant_file):
                #    salmon_file = get_salmon_quant(salmon_quant_file)
            #if len(glob.glob(salmon_quant_dir)) > 1:
            #    print("Too big:",glob.glob(salmon_quant_dir))
 
salmon_dir = "/mnt/home/ljcohen/mmetsp_salmon/"
dammit_dir = "/mnt/home/ljcohen/mmetsp_dammit/qsub_files/"
annotations_dir = "/mnt/home/ljcohen/mmetsp_transcriptid_mapping/"
dammit_dirs = os.listdir(dammit_dir)

execute(dammit_dirs,dammit_dir,salmon_dir,annotations_dir)

