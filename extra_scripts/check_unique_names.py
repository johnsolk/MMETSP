import os
import pandas as pd

def get_sample_dictionary(sample_dictionary,filename):
    with open(filename) as outfile:
        for line in outfile:
            line_split=line.split(".")
            #print(line_split)
            if line_split[1].startswith("/MMETSP"):
                mmetsp = line_split[1][1:]
                #print(mmetsp)
                num  = next(outfile).split()[0]
                if mmetsp in sample_dictionary:
                    sample_dictionary[mmetsp].append(num)
                else:
                    sample_dictionary[mmetsp] = [num]
    return sample_dictionary

def build_DataFrame(data_frame, new_data):
    # columns=["n_bases","gc","gc_skew","mean_orf_percent"]
    #frames = [data_frame, new_data]
    #data_frame = pd.concat(frames)
    data_frame = data_frame.merge(new_data,how='outer',left_index='index',right_index='index')
    return data_frame

def get_table(sample_dictionary):
    data_frame_new = pd.DataFrame.from_dict(sample_dictionary,orient='index')
    #print(data_frame_new.head())
    return data_frame_new
 
# separately, get total contigs from n_seqs from assembles.csv transrate files
# separately, get total names and unique names

# put all of these stats into one table
annotation_stats_files = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/"
total_annotated_contigs = annotation_stats_files + "total_contigs"
total_OrthoDB = annotation_stats_files + "total_OrthoDB"
total_Pfam = annotation_stats_files + "total_Pfam"
total_Rfam = annotation_stats_files + "total_Rfam"
# these files were sorted by e-value then the top annotation was chosen
# these are the annotation stats for these reduced annotations
# there should be one annotation per contig
unique_annotations = annotation_stats_files + "unique_annotations"
unique_OrthoDB = annotation_stats_files + "unique_OrthoDB"
unique_Pfam = annotation_stats_files + "unique_Pfam"
unique_Rfam = annotation_stats_files + "unique_Rfam"
# these are the annotations for contigs with false crbb with ncgr ref
# these are reduced, so one annotation per contig chosen with same method as above
false_crbb_num_annotations = annotation_stats_files + "false_crbb_num_transcripts"
false_crbb_unique_annotations = annotation_stats_files + "false_crbb_unique_annotations"
false_crbb_OrthoDB = annotation_stats_files + "false_crbb_OrthoDB"
false_crbb_Pfam = annotation_stats_files + "false_crbb_Pfam"
false_crbb_Rfam = annotation_stats_files + "false_crbb_Rfam"
data_frame = pd.DataFrame()
annotation_files = [false_crbb_num_annotations]
#annotation_files = [total_annotated_contigs,unique_annotations,false_crbb_unique_annotations,total_OrthoDB,unique_OrthoDB,false_crbb_OrthoDB,total_Pfam,unique_Pfam,false_crbb_Pfam,total_Rfam,unique_Rfam,false_crbb_Rfam]
for annotation_file in annotation_files:
    print(annotation_file)
    sample_dictionary = {}
    sample_dictionary=get_sample_dictionary(sample_dictionary,annotation_file)
    #print(sample_dictionary)
    data_frame_new = get_table(sample_dictionary)
    data_frame = build_DataFrame(data_frame,data_frame_new) 
#data_frame.columns = ['total_annotated_contigs','unique_annotations','annotations_w_false_crbb','total_OrthoDB','unique_OrthoDB','false_crbb_OrthoDB','total_Pfam','unique_Pfam','false_crbb_Pfam','total_Rfam','unique_Rfam','false_crbb_Rfam']
data_frame.columns = ['false_crbb_num_transcripts']
print(data_frame.head())
#out_filename = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/annotation_stats.csv"
out_filename = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/false_crbb.csv"
data_frame.to_csv(out_filename)
