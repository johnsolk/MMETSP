setwd("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/")
transrate<-read.csv("transrate_scores.csv")
transrate_reference<-read.csv("transrate_reference_scores_cds.csv")
busco_scores<-read.csv("busco_scores_MMETSP.csv")
reads<-read.table("trimmomatic_reads_table.txt",sep="\t",header=TRUE)
MMETSP_ncbi<-read.csv("../SraRunInfo.csv")
mmetsp_id<-read.table("../imicrobe/MMETSP_list",sep="\t",header=TRUE)


head(transrate)
head(transrate_reference)
head(busco_scores)
head(reads)
head(MMETSP_ncbi)
head(mmetsp_id)

evaluation_matrix_1<-merge(transrate,transrate_reference,by="Run")
evaluation_matrix_2<-merge(evaluation_matrix_1,busco_scores,by="Run")
evaluation_matrix_3<-merge(evaluation_matrix_2,reads,by="Run")
evaluation_matrix_4<-merge(evaluation_matrix_3,MMETSP_ncbi,by="Run")
evaluation_matrix<-merge(evaluation_matrix_4,mmetsp_id,by="SampleName")

write.csv(evaluation_matrix,"MMETSP_evaluation_matrix.csv")
colnames(evaluation_matrix)
data<-evaluation_matrix[,c(1,2,94,4,8,67,72,43,44,19,26,55,142,143,93,149,148,151)]
colnames(data)
data_reads<-data[,c(3,8,15,7,12,6,13)]
head(data_reads)
write.csv(data_reads,"plotting_data.csv")
