# Script to run nested for loop over all species and all diamond directories 

outdir=diamond_out/
mkdir $outdir
for fa in Species*.fa
do
	# loop over all species (numbered versions created by orthoFinder)
	echo "Comparing $fa against all other species"
	fnum=${fa//[a-Z.]/}
	
	for db in ../diamond/*.dmnd
	do
		# loop over all diamond databases for the blast
		dbnum=${db//[a-Z.\/]/}
		fout=${outdir}${fnum}_${dbnum}
		if [[ ! -a ${fout}.daa ]]
		then	
			diamond blastp -d $db -q $fa -p 32 -k 500 -a ${outdir}${fnum}_${dbnum} 
		fi

		# run diamond blastp with default parameters ; 
		# set max target sequencesto 500; blosum62
		# diamond blastp -d $db -q $fa -p 32 -k 500 -a ${outdir}${fnum}_${dbnum}	
	done
done


