#!/usr/bin/env python

from __future__ import print_function

def lines(filename):
	count = 0
	cluster_name = ""
	for line in  open(filename,"rU"):
		line = line.rstrip()
		if line.startswith(">"):
			if count >= 1:
				print("{}\t{}".format(cluster_name,count))
				cluster_name = line.strip(">")
				count = 0
		else:	
			count += 1
	if count >= 1:
		print("{}\t{}".format(cluster_name,count))					
		
filename="MMETSP.pep_clu_9.fasta"
lines(filename)
