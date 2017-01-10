import os
import os.path
from os.path import basename
import subprocess
from subprocess import Popen, PIPE
# custom Lisa module
import clusterfunc_py3


def fix_fasta(trinity_fasta, trinity_dir, sra):
    trinity_out = trinity_dir + sra + ".Trinity.fixed.fa"
    fix = """
sed -e "s/^>/>{}_/" {} | sed 's_|_-_g' | sed "s/\s.*$//" > {}
""".format(sra, trinity_fasta, trinity_out, trinity_out, trinity_out)
    return fix,trinity_out


def transdecoder_LongOrf(transdecoderdir, trinity_fasta):
    trans_command = """
TransDecoder.LongOrfs -t {} -m 100
""".format(trinity_fasta)
    return trans_command


def transdecoder_Predict(transdecoderdir, trinity_fasta_prefix):
    trans_predict_command = """
TransDecoder.Predict -t {}
""".format(trinity_fasta_prefix)
    return trans_predict_command

def get_longest_ORF(transdecoderdir, trinity_fasta):
    longest_orf_command = """
get_longest_ORF_per_transcript.pl {}.transdecoder.pep > {}.transdecoder.pep.longest.pep
""".format(trinity_fasta, trinity_fasta)
    return longest_orf_command


def fix(transdecoderdir, trinity_fasta, sra, new_trinity_fasta):
    fix_command = """
sed -e 's/>.*::SRR/>SRR/' {}{}.transdecoder.pep.longest.pep | sed -e 's/::.*//' | sed 's/\*//g'i > {}{}.Trinity.pep.longest
""".format(transdecoderdir, trinity_fasta, new_trinity_fasta, sra)
    return fix_command

def execute(fasta_dir,transdecoder_dir):
    fasta_files = os.listdir(fasta_dir)
    for fasta_file_short in fasta_files:
        fasta_file = fasta_dir + fasta_file_short
        mmetsp  = fasta_file_short.split(".")[0]
        dir_string = "cd "+transdecoder_dir
        fix_string,trinity_fixed_fasta = fix_fasta(fasta_file, transdecoder_dir, mmetsp)
        trans_command = transdecoder_LongOrf(transdecoder_dir,trinity_fixed_fasta)
        trans_predict_command = transdecoder_Predict(transdecoder_dir,trinity_fixed_fasta)
        longest_orf_command = get_longest_ORF(transdecoder_dir,trinity_fixed_fasta)
        fix_command = fix(transdecoder_dir,trinity_fixed_fasta,mmetsp,trinity_fixed_fasta)
        module_name_list = ["TransDecoder/3.0.0"]
        commands = [dir_string,fix_string,trans_command,trans_predict_command,longest_orf_command]
        process_name = "transdecoder"
        module_name_list = ""
        filename = mmetsp
        clusterfunc_py3.qsub_file(transdecoder_dir, process_name,module_name_list, filename, commands)


fasta_dir = "/mnt/research/ged/lisa/dammit_annotations/fasta/"
transdecoder_dir = "/mnt/research/ged/lisa/dammit_annotations/transdecoder/"
execute(fasta_dir,transdecoder_dir)
