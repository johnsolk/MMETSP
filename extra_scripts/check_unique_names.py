import os

name_files_dir = "/mnt/home/ljcohen/mmetsp_name_id/"
names = {}
name_files_short = os.listdir(name_files_dir)
name_files = []
for name_filename in name_files_short:
    name_file_long = name_files_dir + name_filename
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
for mmetsp_entry in names:
    print(mmetsp_entry)
    myset = set(names[mmetsp_entry])
    newlist = list(myset)
    print("Unique:",len(newlist))
    print("Total:",len(names[mmetsp_entry]))
