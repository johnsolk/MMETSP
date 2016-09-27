setwd("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/")

transrate<-read.csv("assembly_evaluation_data/transrate_scores.csv")
transrate_reference<-read.csv("assembly_evaluation_data/transrate_reference_scores_nt.csv")
busco_scores<-read.csv("assembly_evaluation_data/busco_scores.csv")
reads<-read.table("assembly_evaluation_data/trimmomatic_reads_table.txt",sep="\t",header=TRUE)
unique_kmers<-read.csv("assembly_evaluation_data/unique_kmers.txt",sep="\t",header=TRUE)
MMETSP_ncbi<-read.csv("SraRunInfo.csv")
mmetsp_id<-read.table("imicrobe/MMETSP_list",sep="\t",header=TRUE)


head(transrate)
dim(transrate)
head(transrate_reference)
dim(transrate_reference)
head(busco_scores)
dim(busco_scores)
head(reads)
dim(reads)
head(unique_kmers)
dim(unique_kmers)
head(MMETSP_ncbi)
dim(MMETSP_ncbi)
head(mmetsp_id)
dim(mmetsp_id) # this is only 176

evaluation_matrix_1<-merge(transrate,transrate_reference,by="Run")
evaluation_matrix_2<-merge(evaluation_matrix_1,busco_scores,by="Run")
evaluation_matrix_3<-merge(evaluation_matrix_2,reads,by="Run")
evaluation_matrix_4<-merge(evaluation_matrix_3,unique_kmers,by="Run")
evaluation_matrix_5<-merge(evaluation_matrix_4,MMETSP_ncbi,by="Run")
evaluation_matrix<-evaluation_matrix_5
dim(evaluation_matrix)
# wait to do this until later when there are more rows
# evaluation_matrix<-merge(evaluation_matrix_5,mmetsp_id,by="SampleName")

write.csv(evaluation_matrix,"assembly_evaluation_data/MMETSP_evaluation_matrix.csv")
colnames(evaluation_matrix)
data<-evaluation_matrix[,c(1,2,94,4,8,67,72,43,44,19,26,55,142,143,93,149,148,151)]
colnames(data)
data_reads<-data[,c(3,8,15,7,12,6,13)]
head(data_reads)
write.csv(data_reads,"plotting_data.csv")
