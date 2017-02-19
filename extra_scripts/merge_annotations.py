import os
import pandas as pd

def build_DataFrame(data_frame, new_data):
    data_frame = data_frame.merge(new_data,how='outer',left_index='index',right_index='index')
    return data_frame

def get_table(annotation_file):
    data_frame_all = pd.read_csv(annotation_file,index_col = "seqid")
    data_frame_new = data_frame_all[["Name"]]
    return data_frame_new
 
# put all of these names into one table
annotation_names_dir= "/mnt/home/ljcohen/mmetsp_unique_annotations/"
annotation_files = os.listdir(annotation_names_dir)
data_frame = pd.DataFrame()
data_frame_columns = []
for annotation_file in annotation_files:
    mmetsp = annotation_file.split(".")[0]
    annotation_file = annotation_names_dir + annotation_file
    print(annotation_file)
    data_frame_columns.append(mmetsp)
    data_frame_new = get_table(annotation_file)
    data_frame = build_DataFrame(data_frame,data_frame_new) 
data_frame.columns = data_frame_columns
print(data_frame.head())
out_filename = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/annotation_names_by_transcript.csv"
data_frame.to_csv(out_filename)
