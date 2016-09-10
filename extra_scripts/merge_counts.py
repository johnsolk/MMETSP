#!/usr/bin/env python

#USAGE: python merge_counts.py dry/ dry.counts

import os
import sys
from os import path
import pandas as pd


# get txp names as index
listofsamples = os.listdir(sys.argv[1])
quants = {}
data = None
for sample in listofsamples:
    if os.path.isdir(sys.argv[1]+sample):
        if os.path.isfile(sys.argv[1]+sample+"/quant.sf"):
            quant_file = sys.argv[1]+sample+"/quant.sf"
            data=pd.DataFrame.from_csv(quant_file,sep='\t')
            numreads = data['NumReads']
            quants[sample] = numreads

counts = pd.DataFrame.from_dict(quants)
counts.set_index(data.index,inplace=True)
counts.to_csv(sys.argv[2])
