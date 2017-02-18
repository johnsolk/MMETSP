import pandas as pd
import os
from dammit.fileio.gff3 import GFF3Parser

# for each mmetsp id
# for each transcript_id
# grab all Pfam ID from dammit gff
# check with pfam2go mapping file
# output .csv with MMETSP, transcript_id,Pfam,GO

def get_annotations(false_annotations_dir,dammit_dir,contig_dict):
    # make a new file with all annotations for ids
    for mmetsp in contig_dict:
        print(mmetsp)
        dammit_gff = dammit_dir + mmetsp + ".trinity_out_2.2.0.Trinity.fasta.dammit" + "/" + mmetsp + ".trinity_out_2.2.0.Trinity.fasta.dammit.gff3"
        if os.path.isfile(dammit_gff):
            #print(dammit_gff)
            annotations = GFF3Parser(filename=dammit_gff).read()
            if 'Name' in annotations.columns:
                all_names = annotations.sort_values(by=['seqid', 'score'], ascending=True).query('score < 1e-05').drop_duplicates(subset='seqid')[['seqid', 'source','Dbxref','Name']].dropna()
                #all_names = annotations.sort_values(by=['seqid'],ascending=True)[['seqid','Name']].dropna()
                Dbxref_names = all_names[all_names['Dbxref'].str.startswith('"Pfam')]
                Dbxref_names['Dbxref'] = Dbxref_names['Dbxref'].map(lambda x: x.lstrip('"').rstrip('"'))
                all_names_out = false_annotations_dir + mmetsp + '.false_crbb_annotations.csv'
                false_names.to_csv(all_names_out)
                print("Written:",all_names_out)
            else:
                print("Missing:",dammit_gff)

def make_false_dict(contig_files,contig_dir):
    contig_dict = {}
    # Titus mentioned to make sure CRBB is not the problem
    # check in NCGR to make sure contig is not present
    # how to do this?
    # dammit annotations?
    # blast?
    for contig_file in contig_files:
        mmetsp = contig_file.split(".")[0]
        if contig_file.endswith(contig_file):
            contig_file = contig_dir + contig_file
            print(contig_file)
            dib_v_ncgr = pd.read_csv(contig_file)
            # does length matter?
            # 'length'
            # false_crbb_long= false_crbb.loc[false_crbb['orf_length'] >= 100]
            false_crbb = dib_v_ncgr.loc[dib_v_ncgr['has_crb'] == False]
            false_crbb_id = false_crbb['contig_name'].tolist()   
            for transcript in false_crbb_id:
                if mmetsp in contig_dict:
                    contig_dict[mmetsp].append(transcript.split("-")[2])
                else:
                    contig_dict[mmetsp]=[transcript.split("-")[2]]
    return contig_dict

orthodb_file = "/mnt/research/ged/data/dammitdb/aa_seq_euk.fasta"
pfam_file = "/mnt/home/ljcohen/GO_mapping/pfam2go"
false_annotations_dir = "/mnt/home/ljcohen/mmetsp_extra_stuff_evalue/"
contig_dir = "/mnt/home/ljcohen/mmetsp_transrate_ref_dib.zenodo_v_ncgr.nt_contigs/"
contig_files = os.listdir(contig_dir)
dammit_dir = "/mnt/home/ljcohen/mmetsp_dammit/qsub_files/"
contig_dict = make_false_dict(contig_files,contig_dir)
#for mmetsp in contig_dict:
#    print(mmetsp)
#    print(len(contig_dict[mmetsp]))
get_annotations(false_annotations_dir,dammit_dir,contig_dict)
