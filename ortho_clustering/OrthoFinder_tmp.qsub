#!/bin/bash
#PBS -l walltime=4:00:00,nodes=4:ppn=4
#PBS -l mem=1GB
#PBS -j oe
#PBS -A ged
#PBS -M ljcohen@msu.edu
#PBS -m ae
#PBS -W umask=027
set -o nounset
set -o errexit
set -o pipefail
set -x
cd ${PBS_O_WORKDIR}

module load GNU/4.4.5
module load OrthoFinder/2015
module load SciPy
module load NumPy
export MKL_NUM_THREADS=4
python /opt/software/OrthoFinder/2015--GCC-4.4.5/bin/orthofinder.py -f /mnt/scratch/ljcohen/pep_tmp/ -t 16




#qstat -f ${PBS_JOBID}
#cat ${PBS_NODEFILE} # Output Contents of the PBS NODEFILE
#env | grep PBS # Print out values of the current jobs PBS environment variables
