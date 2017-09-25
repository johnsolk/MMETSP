import os
import pandas as pd


def get_unique_names_overall(names_file):
    transcript_counts_dictionary = {}
    transcripts_names = pd.read_csv(names_file)
    transcripts_names = transcripts_names.set_index(['seqid'])
    transcripts_names = transcripts_names.astype(str)
    print(transcripts_names.shape)
    for mmetsp in transcripts_names:
        print(mmetsp)
        temp_transcript_cache = []
        for transcript in transcripts_names[mmetsp]:
            if transcript not in temp_transcript_cache:
                if transcript in transcript_counts_dictionary:
                    transcript_counts_dictionary[transcript] += 1
                    temp_transcript_cache.append(transcript)
                else:
                    transcript_counts_dictionary[transcript] = 1
                    temp_transcript_cache.append(transcript)
    return transcript_counts_dictionary

def make_out_file(out_file,sample_dictionary):
    header=["SampleName","total_annotation_names","unique_annotation_names"]
    with open(out_file,"w") as datafile:
        datafile.write("\t".join(header))
        datafile.write("\n")
        for sample in sample_dictionary:
            datafile.write(sample+"\t")
            annotations = sample_dictionary[sample]
            print(annotations)
            results = list(map(str, annotations))
            datafile.write("\t".join(results))
            datafile.write("\n")
    datafile.close()

names_file = "/mnt/home/ljcohen/annotation_names_by_transcript.csv"
out_file = "/mnt/home/ljcohen/MMETSP/assembly_evaluation_data/intersect_names"
transcript_counts_dictionary = get_unique_names_overall(names_file)
print(len(transcript_counts_dictionary.keys()))
#for transcript in transcript_counts_dictionary:
#    if transcript_counts_dictionary[transcript] >= 600:
#        print(transcript,":",transcript_counts_dictionary[transcript])


#transcript_counts = pd.DataFrame.from_dict(transcript_counts_dictionary,orient='index')
#transcript_counts.columns = ['count_allMMETSP']
#transcript_counts.sort(columns = 'count_allMMETSP', ascending = False)
#transcript_counts.to_csv("../assembly_evaluation_data/MMETSP_common_gene_names.csv")
print("Written: ../assembly_evaluation_data/MMETSP_common_gene_names.csv")
#for gene in unique_dictionary:
#    print(gene,":",gene_counts_dictionary[gene])


#make_out_file(out_file,unique_dictionary)
#print("Written:",make_out_file)
