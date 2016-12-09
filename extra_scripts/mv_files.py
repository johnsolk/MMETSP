import os
from os import path

mmetsp_dir = "/mnt/scratch/ljcohen/mmetsp/"
sra_dir = "/mnt/scratch/ljcohen/mmetsp_sra/"


list_of_dirs = os.listdir("/mnt/scratch/ljcohen/special_flowers/")
for mmetsp in list_of_dirs:
	srr = []
	if mmetsp.startswith("MMETSP"):
		new_mmetsp_dir = mmetsp_dir + mmetsp + "/"
		files = os.listdir(new_mmetsp_dir)
		for filename in files:
			if filename.endswith(".fasta"):
				if filename.startswith("MMETSP") == False:
					genus_species = "_".join(filename.split("_")[0:2])
					new_sra_dir = sra_dir + genus_species
			if filename.startswith("SRR"):
				srr.append(filename)
	print genus_species
	print srr
