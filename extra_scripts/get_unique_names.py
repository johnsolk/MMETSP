import os

def get_unique_names_overall(names_files_dir):
    names = {}
    name_files_short = os.listdir(names_files_dir)
    name_files = []
    for name_filename in name_files_short:
        name_file_long = names_files_dir + name_filename
        name_files.append(name_file_long)
    for name_file in name_files:
        mmetsp = name_file.split(".")[0].split("/")[5]
        with open(name_file) as filename:
            for line in filename:
                if line.startswith("Name"):
                    if line.split("=")[1].startswith("ORF") == False:
                        if mmetsp in names:
                            names[mmetsp].append(line)
                        else:
                            names[mmetsp] = [line]
    unique_dict = {}
    for mmetsp_entry in names:
        print(mmetsp_entry)
        myset = set(names[mmetsp_entry])
        newlist = list(myset)
        unique = len(newlist)
        # this number should match total_contigs
        total = len(names[mmetsp_entry])
        unique_dict[mmetsp_entry] = [total]
        unique_dict[mmetsp_entry].append(unique)
    return unique_dict

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

names_files_dir = "/mnt/home/ljcohen/mmetsp_name_id/"
out_file = "/mnt/home/ljcohen/imicrobe_unique_names.csv"
unique_dictionary = get_unique_names_overall(names_files_dir)
make_out_file(out_file,unique_dictionary)
print("Written:",make_out_file)
