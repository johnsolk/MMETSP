import fnmatch
import os
import os.path
# custom Lisa module
import clusterfunc_py3

def get_data(thefile):
    count = 0
    mmetsp_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_mmetsp = headerline.index("SampleName")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            mmetsp = line_data[position_mmetsp]
            test_mmetsp = mmetsp.split("_")
            if len(test_mmetsp) > 1:
                mmetsp = test_mmetsp[0]
            name_read_tuple = (name, read_type)
            if name_read_tuple in mmetsp_data.keys():
                if mmetsp in mmetsp_data[name_read_tuple]:
                    print("url already exists:", ftp)
                else:
                    mmetsp_data[name_read_tuple].append(mmetsp)
            else:
                mmetsp_data[name_read_tuple] = [mmetsp]
        return mmetsp_data

def get_head_command(SRA, full_filename, filename):
     #Might be obsolete if syrah works
    head_command="""
head -4000000 {} > /mnt/scratch/ljcohen/mmetsp_sourmash/{}.head
""".format(full_filename,filename)
    commands = [head_command]
    process_name = "head"
    module_name_list = [""]
    filename = SRA
    #clusterfunc.qsub_file("/mnt/scratch/ljcohen/mmetsp_sourmash/",
    #                          process_name, module_name_list, filename, commands)


def get_syrah_reads(trimdir, sra, mmetsp,sourmash_dir_syrah):
    trim_1P = trimdir + sra + ".trim_1P.fq"
    trim_2P = trimdir + sra + ".trim_2P.fq"
    if os.path.isfile(trim_1P) and os.path.isfile(trim_2P):
        syrah_command = """
cat {} | /mnt/home/ljcohen/bin/syrah/syrah | sourmash compute -k 21 - -o {}{}.trim_1P.syrah.sig
cat {} | /mnt/home/ljcohen/bin/syrah/syrah | sourmash compute -k 21 - -o {}{}.trim_2P.syrah.sig
""".format(trim_1P,sourmash_dir_syrah,mmetsp,trim_2P,sourmash_dir_syrah,mmetsp)     
        print(syrah_command)
    else:
        print("trimfiles not present:",trim_1P,trim_2P)

def get_sourmash_command(mmetsp):
    sourmash_command="""
sourmash compute --dna /mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/{}.trinity_out_2.2.0.Trinity.fasta -k 21 --name-from-first
""".format(mmetsp)
    commands = [sourmash_command]
    process_name = "sourmash"
    module_name_list = ""
    filename = mmetsp
    print(sourmash_command)
    #clusterfunc_py3.qsub_file("/mnt/home/ljcohen/mmetsp_sourmash/",process_name, module_name_list, filename, commands)

def execute(mmetsp_data, basedir, assemblydir,assemblies,sourmash_dir,sourmash_dir_syrah):
    finished = []
    submitted = []
    missing = []
    special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
    for item in mmetsp_data.keys():
        # print item
        sra = item[1]
        organism = item[0].replace("'","")
        org_seq_dir = basedir + organism + "/"
        mmetsp = mmetsp_data[item][0]
        if mmetsp not in special_flowers:
            sample = "_".join(item).replace("'","") + "_" + mmetsp
            print(mmetsp)
            mmetsp_assembly = [s for s in assemblies if s.startswith(mmetsp)]
            if len(mmetsp_assembly)==0:
                print("Assembly not present:",mmetsp_assembly)
            else:
                print(mmetsp_assembly)
                newdir = org_seq_dir + sra + "/"
                trimdir = newdir + "trim/"
                trinity_fasta = assemblydir + mmetsp_assembly[0]    
                get_sourmash_command(mmetsp)
                get_syrah_reads(trimdir, sra, mmetsp,sourmash_dir_syrah) 
	
assemblydir = "/mnt/home/ljcohen/mmetsp_assemblies_trinity2.2.0/"
datafile = "SraRunInfo_719.csv"
basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
sourmash_dir = "/mnt/scratch/ljcohen/mmetsp_sourmash/"
sourmash_dir_syrah = "/mnt/home/ljcohen/mmetsp_sourmash/syrah/"
mmetsp_data = get_data(datafile)
print(mmetsp_data)
assemblies = os.listdir(assemblydir)
mmetsp_data = get_data(datafile)
execute(mmetsp_data, basedir, assemblydir,assemblies,sourmash_dir,sourmash_dir_syrah)
