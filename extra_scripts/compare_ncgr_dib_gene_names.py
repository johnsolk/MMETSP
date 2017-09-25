import pandas as pd
import os
from dammit.fileio.gff3 import GFF3Parser

def compare_names(dib_compare_dir,ncgr_compare_dir,mmetsp,ncgr_file,dib_file):
    ncgr = pd.read_csv(ncgr_file) 
    dib = pd.read_csv(dib_file)
    new_dib = dib[~dib.Name.isin(ncgr.Name.values)]
    new_ncgr =ncgr[~ncgr.Name.isin(dib.Name.values)]
    new_ncgr_file = ncgr_compare_dir + mmetsp + ".unique_names_v_dib.csv"
    new_dib_file = dib_compare_dir + mmetsp + ".unique_names_v_ncgr.csv"
    new_ncgr.to_csv(new_ncgr_file)
    new_dib.to_csv(new_dib_file)
    print("Written:",new_ncgr_file)
    print("Size:",new_ncgr.shape)
    print("Written:",new_dib_file)
    print("Size:",new_dib.shape)

def get_mmetsp_assembly(count,ncgr_files,mmetsp,dib_file):
    file_list = [s for s in ncgr_files if s.startswith(mmetsp)]
    if len(file_list) > 0:
        ncgr_file = file_list[0]
        print("NCGR:",ncgr_file)
        print("MMETSP:",dib_file)
        count += 1
        return count,ncgr_file
    else:
        print("Don't have NCGR dammit annotations yet:",mmetsp)
        ncgr_file = ""
        return count,ncgr_file

dib_annotations = "/mnt/home/ljcohen/mmetsp_unique_annotations/"
ncgr_annotations = "/mnt/home/ljcohen/dammit_imicrobe_genenames/"
ncgr_compare_dir = "/mnt/home/ljcohen/ncgr_unique_names/"
dib_compare_dir = "/mnt/home/ljcohen/dib_unique_names/"
ncgr_files= os.listdir(ncgr_annotations)
dib_files = os.listdir(dib_annotations)
count = 0
for dib_file in dib_files:
    mmetsp = dib_file.split(".")[0]
    count,ncgr_file = get_mmetsp_assembly(count,ncgr_files,mmetsp,dib_file)
    if ncgr_file:
        ncgr_filename = ncgr_annotations + ncgr_file
        dib_filename = dib_annotations + dib_file
        compare_names(dib_compare_dir,ncgr_compare_dir,mmetsp,ncgr_filename,dib_filename)
print(count)
