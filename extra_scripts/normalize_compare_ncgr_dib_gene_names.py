import pandas as pd
import os
from dammit.fileio.gff3 import GFF3Parser


def get_contig_num(contig_names,mmetsp):
    frame = pd.read_csv(contig_names)
    nums  = frame.loc[frame['SampleName'] == mmetsp]
    if nums.empty:
       print('empty:',contig_names)
       contig_num = 0
       return contig_num
    else:
       contig_num = nums.iloc[0]['n_seqs']
       print(contig_names,mmetsp,":",contig_num)
       return contig_num

def compare_names(dib_contig_num,ncgr_contig_num,unique_name_counts,dib_compare_dir,ncgr_compare_dir,mmetsp,ncgr_file,dib_file):
    ncgr = pd.read_csv(ncgr_file) 
    dib = pd.read_csv(dib_file)
    new_dib = dib[~dib.Name.isin(ncgr.Name.values)]
    new_ncgr =ncgr[~ncgr.Name.isin(dib.Name.values)]
    new_ncgr_file = ncgr_compare_dir + mmetsp + ".unique_names_v_dib.csv"
    new_dib_file = dib_compare_dir + mmetsp + ".unique_names_v_ncgr.csv"
    new_ncgr.to_csv(new_ncgr_file)
    new_dib.to_csv(new_dib_file)
    ncgr_unique = new_ncgr.shape[0]
    dib_unique = new_dib.shape[0]
    if ncgr_contig_num != 0 and dib_contig_num != 0:
        norm_ncgr_unique_counts = ncgr_unique / ncgr_contig_num
        norm_dib_unique_counts = dib_unique / dib_contig_num
        print(norm_ncgr_unique_counts,norm_dib_unique_counts)
        if mmetsp != None and norm_ncgr_unique_counts != None and norm_dib_unique_counts != None:
            print(mmetsp)
            print(norm_ncgr_unique_counts,norm_dib_unique_counts)
            print(unique_name_counts)
            unique_name_counts.append([mmetsp,norm_ncgr_unique_counts,norm_dib_unique_counts])
            print("Written:",new_ncgr_file)
            print("Size:",new_ncgr.shape)
            print("Written:",new_dib_file)
            print("Size:",new_dib.shape)
            return unique_name_counts
        else:
            print("This was 'None':",mmetsp,norm_ncgr_unique_counts,norm_dib_unique_counts)
            return unique_name_counts
    else:
        print("Zero:",ncgr_contig_num,dib_contig_num)
        return unique_name_counts

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

dib_contig_nums = "~/MMETSP/assembly_evaluation_data/transrate_reference_scores_cds.csv"
ncgr_contig_nums = "~/MMETSP/assembly_evaluation_data/transrate_imicrobe_scores.csv"


count = 0
unique_name_counts = []
for dib_file in dib_files:
    mmetsp = dib_file.split(".")[0]
    count,ncgr_file = get_mmetsp_assembly(count,ncgr_files,mmetsp,dib_file)
    dib_contig_num = get_contig_num(dib_contig_nums,mmetsp)
    ncgr_contig_num = get_contig_num(ncgr_contig_nums,mmetsp)
    if ncgr_file:
        ncgr_filename = ncgr_annotations + ncgr_file
        dib_filename = dib_annotations + dib_file
        unique_name_counts = compare_names(dib_contig_num,ncgr_contig_num,unique_name_counts,dib_compare_dir,ncgr_compare_dir,mmetsp,ncgr_filename,dib_filename)
print(count)
df = pd.DataFrame(unique_name_counts, columns = ['MMETSP_id','NCGR','DIB'])
df.to_csv("~/MMETSP/assembly_evaluation_data/normalized_unique_gene_names_ncgr_dib.csv")
print("Written: ~/MMETSP/assembly_evaluation_data/normalized_unique_gene_names_ncgr_dib.csv")
