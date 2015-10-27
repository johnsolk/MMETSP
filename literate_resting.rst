This is an initial stab at khmer acceptance testing, based on khmer
protocols/eel pond.  To run, execute the following commands on an AWS
m1.xlarge machine running the ubuntu-trusty-14.04-amd64-server-* 
Amazon Machine Image (AMI) which is one of the featured AMIs. This was
last tested using "ubuntu-trusty-14.04-amd64-server-20140927 (ami-98aa1cf0)"

For more info on khmer, see github.com/dib-lab/khmer, and
khmer.readthedocs.org/.

For more info on khmer-protocols, see github.com/dib-lab/khmer-protocols,
and khmer-protocols.readthedocs.org/.

---

Note that the branch of khmer under test is specified in
mrnaseq/1-quality.txt in the khmer-protocols repository; CTB suggests
that to run an acceptance test against a specific version of khmer, we
create a new branch of khmer-protocols on github.com/dib-lab that
specifies the right version in mrnaseq/1-quality.txt, and then put '-b
branchname' in the clone command below.

---

Do that sudo you do so well::

   sudo chmod a+rwxt /mnt
   sudo apt-get -y install git-core

Next, ::
   
   cd /home/ubuntu
   rm -fr literate-resting khmer-protocols
   git clone https://github.com/dib-lab/literate-resting.git
   git clone https://github.com/dib-lab/khmer-protocols.git -b ctb
   
   cd khmer-protocols/mrnaseq
   
   ## vim 1-quality.rst # change version number on line 49 to match the release to test
   
   for i in [1-3]-*.rst
   do
      /home/ubuntu/literate-resting/scan.py $i || break
   done
   
   ### START MONITORING (in another SSH session)
   
   for i in [1-3]-*.rst.sh
   do
      bash $i |& tee ${i%%.rst.sh}.out || break
   done

---

Successful completion can be checked by hand in two ways, after running::

   /root/literate-resting/scan.py acceptance-3-big-assembly.rst
   bash -e acceptance-3-big-assembly.rst.sh

FIRST, you should see stats output from this command::

   /usr/local/share/khmer/sandbox/assemstats3.py 500 /mnt/work/trinity_out_dir/Trinity.fasta

that looks roughly like this::

   ** cutoff: 500
   N       sum     max     filename
   76      134259  4452    /mnt/work/trinity_out_dir/Trinity.fasta

SECOND the command ::

   grep "zinc transporter" /mnt/blast/trinity.x.mouse

should show more than 20 matches.

---

To run system monitoring::

   sar -u -r -d -o times.dat 1

   sar -d -p -f times.dat > disk.txt
   sar -u -f times.dat > cpu.txt
   sar -r -f times.dat > ram.txt
   gzip *.txt

See github.com/ctb/sartre/ for parsing tools for sar output.
