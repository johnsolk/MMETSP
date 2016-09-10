import os


def log_parse(trimdir):
    print trimdir
    listoffiles = os.listdir(trimdir)
    for i in listoffiles:
        if i.endswith(".log"):
            with open(trimdir + i) as datafile:
                for line in datafile:
                    line_data = line.split()
                    # print line_data
                    if line_data[0] == "Input":
                        print line_data[6]
                        print "Percent both surviving:", line_data[7]
trimdir_list = ["/mnt/mmetsp/subset/trim_combined/",
                "/mnt/mmetsp/subset/trim_TS2/",
                "/mnt/mmetsp/subset/trim_TS3/",
                "/mnt/mmetsp/subset/trim_TS3-2/"]
for trimdir in trimdir_list:
    log_parse(trimdir)
