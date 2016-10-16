# MMETSP

This is a review branch.


[![Binder](http://mybinder.org/badge.svg)](http://mybinder.org/repo/dib-lab/MMETSP)

This is a work-in-progress repository, automating the khmer protocols over a large-scale RNAseq data set:

https://khmer-protocols.readthedocs.org/en/ctb/mrnaseq/

The Marine Microbial Eukaryotic Transcriptome Sequencing Project (MMETSP) data set contains 678 cultured samples of 306 pelagic and endosymbiotic marine eukaryotic species representing more than 40 phyla (Keeling et al. 2014).

Each script takes `SraRunInfo.csv` as input. This file can be obtained for any collection of SRA records from NCBI.

Automated scripts running the protocols:

1. `getdata.py`, download data from NCBI and organize into individual directories for each sample/accession ID
2. `trim_qc.py`, trim reads for quality, interleave reads
3. `diginorm_mmetsp.py`, normalize-by-median and filter-abund from khmer, rename, combined orphans,
4. `assembly.py`, runs Trinity de novo transcriptome assembly software 

Additional scripts:

1. `dammit.py`, annotation https://github.com/camillescott/dammit/tree/master/dammit
2. `salmon.py`, runs salmon reference-free transcript quantification https://github.com/COMBINE-lab/salmon
3. `rapclust.py`, clustering contigs https://github.com/COMBINE-lab/rapclust
4. `busco.py`, assessing assembly and annotation completeness with single-copy orthologs http://busco.ezlab.org/
5. `clusterfunc.py`, cluster control module
6. `sourmash.py`, MinHash signatures to cluster unassembled reads https://github.com/dib-lab/sourmash/tree/v0.9.4
7. `transdecoder.py`, translate nucleotide contigs to amino acid contigs http://transdecoder.github.io/
8. `transrate.py`, evaluate assembly with reads http://hibberdlab.com/transrate/
9. `transrate_reference.py`, evaluate assembly with reference assembly http://hibberdlab.com/transrate/

References:

Keeling et al. 2014: http://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001889

Supporting information with methods description: 

http://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001889#s6

Preliminary assembly protocol run by NCGR:
https://github.com/ncgr/rbpa

NCBI Bioproject accession: PRJNA231566

http://www.ncbi.nlm.nih.gov/bioproject/PRJNA231566/

MMETSP website: http://marinemicroeukaryotes.org/

iMicrobe project with data and combined assembly downloads: http://data.imicrobe.us/project/view/104
