import pandas as pd
import os
from dammit.fileio.gff3 import GFF3Parser

def get_annotations(mmetsp,dammit_gff_file,gene_names_dir,dammit_gff_dir):
    dammit_gff = dammit_gff_dir + dammit_gff_file
    all_names_out = gene_names_dir + mmetsp + ".unique_annotations.csv"
    if os.path.isfile(all_names_out):
       print("Unique annotations already written:",all_names_out)
    else:
        if os.path.isfile(dammit_gff):
            print(dammit_gff)
            annotations = GFF3Parser(filename=dammit_gff).read()
            if 'Name' in annotations.columns and 'Dbxref' in annotations.columns:
                all_names = annotations.sort_values(by=['seqid', 'score'], ascending=True).query('score < 1e-05').drop_duplicates(subset='seqid')[['seqid', 'Name','Dbxref','source']]
                all_names_out = gene_names_dir + mmetsp + ".unique_annotations.csv"
                all_names.to_csv(all_names_out)
                print("Written:",all_names_out)
        else:
            print("Missing:",dammit_gff)

dammit_gff_dir = "/mnt/home/ljcohen/dammit_imicrobe/"
gene_names_dir = "/mnt/home/ljcohen/dammit_imicrobe_genenames/"
dammit_gffs = os.listdir(dammit_gff_dir)
mmetsp_list = []
for dammit_gff in dammit_gffs:
    if dammit_gff.endswith(".gff3"):
        mmetsp = dammit_gff.split(".")[0]
        mmetsp_list.append(mmetsp)
        get_annotations(mmetsp,dammit_gff,gene_names_dir,dammit_gff_dir)
