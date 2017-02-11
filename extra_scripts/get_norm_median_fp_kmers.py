import os
import os.path
import clusterfunc_py3
import pandas as pd

def get_data(thefile):
    count = 0
    url_data = {}
    with open(thefile, "rU") as inputfile:
        headerline = next(inputfile).split(',')
        # print headerline
        position_name = headerline.index("ScientificName")
        position_reads = headerline.index("Run")
        position_ftp = headerline.index("download_path")
        position_mmetsp = headerline.index("SampleName")
        for line in inputfile:
            line_data = line.split(',')
            name = "_".join(line_data[position_name].split())
            read_type = line_data[position_reads]
            ftp = line_data[position_ftp]
            mmetsp = line_data[position_mmetsp]
            name_read_tuple = (name, read_type,mmetsp)
            print(name_read_tuple)
            # check to see if Scientific Name and run exist
            if name_read_tuple in url_data.keys():
                # check to see if ftp exists
                if ftp in url_data[name_read_tuple]:
                    print("url already exists:", ftp)
                else:
                    url_data[name_read_tuple].append(ftp)
            else:
                url_data[name_read_tuple] = [ftp]
        return url_data

def get_sample_dictionary(sample_dictionary,diginorm_outputfile,mmetsp):
    with open(diginorm_outputfile,) as outfile:
        for line in outfile:
            line_split=line.split()
            if len(line_split)>=2:
                if line_split[0].startswith("output") and line_split[2].startswith("orphans"):
                    prev_line_split = prev_line.split()
                    kept = prev_line_split[4]
                    total = prev_line_split[6]
                    perc_kept = prev_line_split[8]
                if line_split[0].startswith("Total"):	
                    num_kmers = line_split[5]
                if line_split[0].startswith("fp"):
                    fp_rate = line_split[5]
                    sample_dictionary[mmetsp]=[kept,total,perc_kept,num_kmers,fp_rate]				
                    print([kept,total,perc_kept,num_kmers,fp_rate])
            prev_line = line
    return sample_dictionary


def diginorm_table(sample_dictionary,fprate_filename):
    data_frame = pd.DataFrame.from_dict(sample_dictionary,orient='index')
    data_frame.columns = ["kept","total","perc_kept","num_kmers","fp_rate"]
    data_frame.to_csv(fprate_filename)
    print("Diginorm stats written:",fprate_filename)


def execute(url_data,fprate_filename,basedir):
    sample_dictionary = {}
    complete = 0
    not_complete = []
    not_exist = []
    special_flowers = ["MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922"]
    for item in url_data:
        organism = item[0].replace("'","")
        org_seq_dir = basedir + organism + "/"
        sra = item[1]
        mmetsp = item[2]
        if mmetsp in special_flowers:
           print("Special flower:",mmetsp)
        else:
            newdir = org_seq_dir + sra + "/"
            trimdir = newdir + "trim/qsub_files/"
            diginormdir = newdir + "diginorm/qsub_files/"
            if os.path.isdir(diginormdir):
                output_files = os.listdir(diginormdir)
                diginorm_outputfiles = [s for s in output_files if s.startswith("diginorm") and s.split(".")[-1].startswith("o")]
                if len(diginorm_outputfiles)==0:
                    print("diginorm output not available:",diginormdir)
                else:
                    print(diginorm_outputfiles)
                    diginorm_outputfiles = sorted(diginorm_outputfiles)
                    print(diginorm_outputfiles)
                    diginorm_outputfile = diginormdir + diginorm_outputfiles[-1]
                    matching_string = "...saving to"
                    with open(diginorm_outputfile) as f:
                        content = f.readlines()
                    diginorm_content = [m for m in content if matching_string in m]
                    if len(diginorm_content)!=0:
                        print("Diginorm completed!",diginormdir)
                        complete +=1
                        sample_dictionary = get_sample_dictionary(sample_dictionary,diginorm_outputfile,mmetsp)
                    else:
                        print("Diginorm not complete:",diginormdir)
                        not_complete.append(diginormdir)
            else:
                print("Does not exist:",diginormdir)
                not_exist.append(diginormdir)
    print(sample_dictionary)
    diginorm_table(sample_dictionary,fprate_filename)
    print(len(sample_dictionary.keys()))
    return complete,not_complete,not_exist
        
basedir = "/mnt/scratch/ljcohen/mmetsp_sra/"
datafile = "../SraRunInfo_719.csv"
fprate_filename = "../assembly_evaluation_data/fp_rate_diginorm.csv"
url_data = get_data(datafile)
print(url_data)
complete,not_complete,not_exist = execute(url_data,fprate_filename,basedir)
print("Complete:",complete)
print("Diginorm not complete:",len(not_complete))
print("Does not exist:",len(not_exist))

