library(RColorBrewer)
setwd("~/Documents/UCDavis/dib/MMETSP")
Cols = function(vec){
  #cols=palette(brewer.pal(n=7,name="Dark2"))
  cols=rainbow(length(unique(vec)))
  return(cols[as.numeric(as.factor(vec))])}


dib_ncgr_kmers <- read.csv("assembly_evaluation_data/unique_kmers.csv")
unique_dammit_names <- read.csv("assembly_evaluation_data/normalized_unique_gene_names_ncgr_dib.csv")
unique_dammit_names <- unique_dammit_names[,2:4]
colnames(unique_dammit_names) <- c("SampleName","NCGR","DIB")
unique_dammit_names <- merge(dib_ncgr_kmers,unique_dammit_names,by="SampleName")
unique_dammit_names <- unique_dammit_names[,c(1,2,5,6)]
#head(dib_ncgr_kmers)
#dim(dib_ncgr_kmers)
head(unique_dammit_names)
#dim(unique_dammit_names)
special_flowers = c("MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922")
# Only use 7 most common phyla
sub_phy<-c("Bacillariophyta","Dinophyta","Ochrophyta","Haptophyta","Ciliophora","Chlorophyta","Cryptophyta")


dib_ncgr_kmers <- dib_ncgr_kmers[!dib_ncgr_kmers$SampleName %in% special_flowers,]
#dim(dib_ncgr_kmers)
#head(dib_ncgr_kmers)
dib_greater<-dib_ncgr_kmers[which(dib_ncgr_kmers$DIB>dib_ncgr_kmers$NCGR),]
ncgr_greater<-dib_ncgr_kmers[which(dib_ncgr_kmers$NCGR>dib_ncgr_kmers$DIB),]
#dim(dib_greater)
#dim(ncgr_greater)
dib_ncgr_kmers<-dib_ncgr_kmers[dib_ncgr_kmers$Phylum %in% sub_phy,]
pdf("paper/Figure6_unique_kmers.pdf")
#png("paper/Figure6_unique_kmers.png")
plot(dib_ncgr_kmers$Unique_kmers,dib_ncgr_kmers$Unique_kmers_assembly, ylim=c(-1,120000000),xlim=c(-1,120000000),ylab = "DIB unique kmers",xlab="NCGR unique kmers",col=Cols(as.character(dib_ncgr_kmers$Phylum)),pch=19,frame.plot = FALSE)
abline(0,1)
legend(20,125000000,legend=sort(unique(as.character(dib_ncgr_kmers$Phylum))),col=Cols(unique(as.character(dib_ncgr_kmers$Phylum))),cex=0.8, pch=19,bty="n")
dev.off()
plot(dib_ncgr_kmers$Unique_kmers,dib_ncgr_kmers$Unique_kmers_assembly, ylim=c(-1,120000000),xlim=c(-1,120000000),ylab = "DIB unique kmers",xlab="NCGR unique kmers",col=Cols(as.character(dib_ncgr_kmers$Phylum)),pch=19,frame.plot = FALSE)
abline(0,1)
legend(20,125000000,legend=sort(unique(as.character(dib_ncgr_kmers$Phylum))),col=Cols(sort(unique(as.character(dib_ncgr_kmers$Phylum)))),cex=0.8, pch=19,bty="n")

dib_ncgr_kmers <- dib_ncgr_kmers[!dib_ncgr_kmers$SampleName %in% special_flowers,]
dib_ncgr_kmers<-dib_ncgr_kmers[dib_ncgr_kmers$Phylum %in% sub_phy,]
unique(as.character(dib_ncgr_kmers$Phylum))

sub_phy<-c("Bacillariophyta","Dinophyta","Ochrophyta","Haptophyta","Ciliophora","Chlorophyta","Cryptophyta")
unique_dammit_names <- unique_dammit_names[unique_dammit_names$Phylum %in% sub_phy,]
pdf("paper/Figure7_unique_gene_names.pdf",width=11,height=8.5)
#png("paper/Figure7_unique_gene_names.png",width=11,height=8.5)
plot(unique_dammit_names$NCGR,unique_dammit_names$DIB,ylim=c(-0.01,1.1),xlim=c(-0.01,1.1),col=Cols(as.character(unique_dammit_names$Phylum)),pch=19,ylab = "unique names in DIB re-assemblies",xlab="unique names in NCGR assemblies",main="Counts of unique gene names per total number of annotated contigs",frame.plot = FALSE)
abline(0,1)
legend(0,1.1,legend=sort(unique(as.character(unique_dammit_names$Phylum))),col=Cols(as.character(unique_dammit_names$Phylum)),cex=0.8, pch=19,bty="n")
dev.off()
plot(unique_dammit_names$NCGR,unique_dammit_names$DIB,ylim=c(-0.01,1.1),xlim=c(-0.01,1.1),col=Cols(as.character(unique_dammit_names$Phylum)),pch=19,ylab = "unique names in DIB re-assemblies per # annotated contigs",xlab="unique names in NCGR assemblies per # annotated contigs",frame.plot = FALSE)
abline(0,1)
legend(0,1.1,legend=sort(unique(as.character(unique_dammit_names$Phylum))),col=Cols(sort(unique(as.character(unique_dammit_names$Phylum)))),cex=0.8, pch=19,bty="n")

