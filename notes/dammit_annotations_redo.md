There were 104 dammit annotation jobs on MSU HPCC that not complete. (for reasons)

1. Script `check_dammit_annotations.py` checks the number of lines in the original .fasta and compares to the dammit .fasta. If there are differences, the original .fasta is copied to a new directory.

2. Started 10 AWS us-east ami-002f0f6a instances and with dammit installations: 

https://github.com/dib-lab/eel-pond/blob/master/5-annotating.rst

3. Separted 104 files into 10 sets of files to scp to aws instance.

```
mkdir fasta
cd fasta
scp ljcohen@gateway.hpcc.msu.edu:/mnt/home/ljcohen/mmetsp_dammit_redo/MMETSP_redo_1/*.fasta .
```
aws_1:
```
(dammit) ubuntu@ip-172-31-10-59:~/fasta$ ls -lah
total 264M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:39 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:30 ..
-rw-r--r--  1 ubuntu ubuntu  33M Apr  4 18:31 MMETSP1409.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  33M Apr  4 18:31 MMETSP1418.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  29M Apr  4 18:31 MMETSP1423.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  77M Apr  4 18:31 MMETSP1426.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  20M Apr  4 18:31 MMETSP1432.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  15M Apr  4 18:31 MMETSP1460.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:31 MMETSP1465.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 8.4M Apr  4 18:31 MMETSP1472.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:31 MMETSP1473.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  17M Apr  4 18:31 MMETSP1475.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
(dammit) ubuntu@ip-172-31-10-59:~/fasta$ ls -lah *.fasta | wc -l
10
```
aws_2:
```
(dammit) ubuntu@ip-172-31-5-23:~/fasta$ ls -lah *.fasta | wc -l
13
(dammit) ubuntu@ip-172-31-5-23:~/fasta$ ls -lah
total 282M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:39 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:31 ..
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:32 MMETSP1002.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  30M Apr  4 18:32 MMETSP1010.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 9.0M Apr  4 18:32 MMETSP1018.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:32 MMETSP1019.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:32 MMETSP1039.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:32 MMETSP1040.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  43M Apr  4 18:33 MMETSP1055.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  19M Apr  4 18:33 MMETSP1080.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  28M Apr  4 18:33 MMETSP1081.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:33 MMETSP1082.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  15M Apr  4 18:33 MMETSP1085.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  18M Apr  4 18:33 MMETSP1086.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  18M Apr  4 18:33 MMETSP1095.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_3:
```
(dammit) ubuntu@ip-172-31-3-145:~/fasta$ ls -lah *.fasta | wc -l
13
(dammit) ubuntu@ip-172-31-3-145:~/fasta$ ls -lah
total 289M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:49 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:35 ..
-rw-r--r--  1 ubuntu ubuntu  36M Apr  4 18:47 MMETSP0909.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:47 MMETSP0920.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:47 MMETSP0922.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:47 MMETSP0923.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  12M Apr  4 18:48 MMETSP0925.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  16M Apr  4 18:48 MMETSP0933.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  13M Apr  4 18:48 MMETSP0936.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:48 MMETSP0958.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  25M Apr  4 18:48 MMETSP0960.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  27M Apr  4 18:48 MMETSP0961.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  37M Apr  4 18:48 MMETSP0971.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  33M Apr  4 18:49 MMETSP0972.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  28M Apr  4 18:49 MMETSP0975.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_4:
```
(dammit) ubuntu@ip-172-31-2-248:~/fasta$ ls -lah *.fasta | wc -l
8
(dammit) ubuntu@ip-172-31-2-248:~/fasta$ ls -lah
total 324M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:48 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:47 ..
-rw-r--r--  1 ubuntu ubuntu  29M Apr  4 18:48 MMETSP0707.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:48 MMETSP0713.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 7.8M Apr  4 18:48 MMETSP0717.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  29M Apr  4 18:48 MMETSP0751.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  28M Apr  4 18:48 MMETSP0753.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:48 MMETSP0785.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 103M Apr  4 18:48 MMETSP0796.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  81M Apr  4 18:48 MMETSP0797.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_5:
```
(dammit) ubuntu@ip-172-31-13-235:~/fasta$ ls -lah
total 429M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:58 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:58 ..
-rw-r--r--  1 ubuntu ubuntu 100M Apr  4 18:48 MMETSP0648.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 106M Apr  4 18:48 MMETSP0649.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 4.1M Apr  4 18:48 MMETSP0693.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  38M Apr  4 18:48 MMETSP0698.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:48 MMETSP0802.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:48 MMETSP0850.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  27M Apr  4 18:48 MMETSP0852.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  34M Apr  4 18:48 MMETSP0878.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  33M Apr  4 18:48 MMETSP0880.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:48 MMETSP0886.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:48 MMETSP0890.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
(dammit) ubuntu@ip-172-31-13-235:~/fasta$ ls -lah *.fasta | wc -l
11
```
aws_6:
```
(dammit) ubuntu@ip-172-31-4-170:~/fasta$ ls -lah *.fasta | wc -l
10
(dammit) ubuntu@ip-172-31-4-170:~/fasta$ ls -lah
total 428M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:49 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:48 ..
-rw-r--r--  1 ubuntu ubuntu  40M Apr  4 18:49 MMETSP0404.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  34M Apr  4 18:49 MMETSP0416.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  20M Apr  4 18:49 MMETSP0492.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 114M Apr  4 18:49 MMETSP0573.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 127M Apr  4 18:49 MMETSP0574.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  24M Apr  4 18:49 MMETSP1137.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:49 MMETSP1159.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  13M Apr  4 18:49 MMETSP1161.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  20M Apr  4 18:49 MMETSP1165.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  30M Apr  4 18:49 MMETSP1177.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_7:
```
(dammit) ubuntu@ip-172-31-12-10:~/fasta$ ls -lah *.fasta | wc -l
9
(dammit) ubuntu@ip-172-31-12-10:~/fasta$ ls -lah
total 216M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:49 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:49 ..
-rw-r--r--  1 ubuntu ubuntu  33M Apr  4 18:49 MMETSP0319.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:49 MMETSP0322.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  27M Apr  4 18:49 MMETSP0327.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  68M Apr  4 18:49 MMETSP0371.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 4.1M Apr  4 18:49 MMETSP0398.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 4.1M Apr  4 18:49 MMETSP0399.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  18M Apr  4 18:49 MMETSP1345.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  27M Apr  4 18:49 MMETSP1346.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  15M Apr  4 18:49 MMETSP1347.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_8:
```
(dammit) ubuntu@ip-172-31-14-26:~/fasta$ ls -lah *.fasta | wc -l
10
(dammit) ubuntu@ip-172-31-14-26:~/fasta$ ls -lah
total 232M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:51 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:49 ..
-rw-r--r--  1 ubuntu ubuntu  25M Apr  4 18:50 MMETSP0200.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  73M Apr  4 18:50 MMETSP0228.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  28M Apr  4 18:50 MMETSP0295.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  28M Apr  4 18:51 MMETSP0296.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  14M Apr  4 18:51 MMETSP1312.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  14M Apr  4 18:51 MMETSP1316.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 4.0M Apr  4 18:51 MMETSP1325.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:51 MMETSP1329.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  14M Apr  4 18:51 MMETSP1353.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  14M Apr  4 18:51 MMETSP1354.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_9:
```
(dammit) ubuntu@ip-172-31-12-144:~/fasta$ ls -lah *.fasta | wc -l
11
(dammit) ubuntu@ip-172-31-12-144:~/fasta$ ls -lah
total 272M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:52 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:50 ..
-rw-r--r--  1 ubuntu ubuntu  27M Apr  4 18:50 MMETSP0110.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  23M Apr  4 18:50 MMETSP0113.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:50 MMETSP0115.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  66M Apr  4 18:51 MMETSP0117.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  31M Apr  4 18:51 MMETSP0139.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  30M Apr  4 18:51 MMETSP0140.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  31M Apr  4 18:52 MMETSP0142.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  30M Apr  4 18:52 MMETSP0150.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  16M Apr  4 18:52 MMETSP0169.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 1.3M Apr  4 18:52 MMETSP0196.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  11M Apr  4 18:52 MMETSP0197.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
aws_10:
```
(dammit) ubuntu@ip-172-31-11-79:~/fasta$ ls -lah *.fasta | wc -l
9
(dammit) ubuntu@ip-172-31-11-79:~/fasta$ ls -lah
total 306M
drwxrwxr-x  2 ubuntu ubuntu 4.0K Apr  4 18:51 .
drwxr-xr-x 20 ubuntu ubuntu 4.0K Apr  4 18:50 ..
-rw-r--r--  1 ubuntu ubuntu  36M Apr  4 18:51 MMETSP0008.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  29M Apr  4 18:51 MMETSP0020.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 111M Apr  4 18:51 MMETSP0030.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 3.9M Apr  4 18:51 MMETSP0088.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu 4.7M Apr  4 18:51 MMETSP0092.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  40M Apr  4 18:51 MMETSP1385.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  22M Apr  4 18:51 MMETSP1386.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  36M Apr  4 18:51 MMETSP1392.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
-rw-r--r--  1 ubuntu ubuntu  26M Apr  4 18:51 MMETSP1394.trinity_out_2.2.0.Trinity.fasta.renamed.fasta
```
Total: 105 (one extra somewhere...)
aws_1: 10
aws_2: 13
aws_3: 13
aws_4: 8
aws_5: 11
aws_6: 10
aws_7: 9
aws_8: 10
aws_9: 11
aws_10: 10


5. Start screen
```
screen
source ~/.bashrc
source activate dammit
```

6. Ran `dammit annotate` in a loop:

```
for assemblyfile in *.fasta
do
	dammit annotate $assemblyfile --n_threads 12
done
```
