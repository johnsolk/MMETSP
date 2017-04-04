import os
from shutil import copyfile

def get_num_lines(filename):
    with open(filename) as f:
        return len(f.readlines())

dammit_fasta = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0_zenodo/"
dammit_files = os.listdir(dammit_fasta)
trinity_fasta = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0_figshare/"
trinity_files = os.listdir(trinity_fasta)
mismatches = []
copy_dir = "/mnt/home/ljcohen/mmetsp_dammit_redo/"
for trinity_file in trinity_files:
    mmetsp = trinity_file.split(".")[0]
    dammit_file_list = [s for s in dammit_files if s.startswith(mmetsp)]
    if len(dammit_file_list ) > 0:
        dammit_filename = dammit_fasta + dammit_file_list[0]
        trinity_filename = trinity_fasta + trinity_file
        dammit_lines = get_num_lines(dammit_filename)
        trinity_lines = get_num_lines(trinity_filename)
        print("Dammit lines:",dammit_lines)
        print("Trinity lines:",trinity_lines)
        if trinity_lines != dammit_lines:
            mismatches.append(trinity_filename)
            dst = copy_dir + trinity_file
            copyfile(trinity_filename, dst)
print("Number of mismatches:",len(mismatches)) 
