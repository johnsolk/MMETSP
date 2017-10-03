require(graphics)
library(psych) # required for describeBy
library(multcomp)
library(agricolae)
library(RColorBrewer)
library(lattice)
library("tsne")
## MMETSP stats
dib_v_ncgr <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/transrate_reference_trinity2.2.0_v_ncgr.cds.csv")
ncgr_v_dib <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/transrate_reverse_ncgr.nt_v_trinity2.2.0.csv")
dim(dib_v_ncgr)
dim(ncgr_v_dib)
score_ncgr <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/transrate_scores_imicrobe_cds.csv")
score_dib <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/transrate_scores_trinity-2.2.0.csv")
dim(score_ncgr)
dim(score_dib)
# Number of contigs
contigs_dib_v_ncgr <- dib_v_ncgr$n_seqs
contigs_ncgr_v_dib <- ncgr_v_dib$n_seqs
length(contigs_dib_v_ncgr)
length(contigs_ncgr_v_dib)
mean(contigs_dib_v_ncgr)
mean(contigs_ncgr_v_dib)
sd(contigs_dib_v_ncgr)
sd(contigs_ncgr_v_dib)
ks.test(contigs_dib_v_ncgr,contigs_ncgr_v_dib)
# Transrate score
transrate_score_dib <- score_dib$score
transrate_score_ncgr <- score_ncgr$score
length(transrate_score_dib)
length(transrate_score_ncgr)
mean(transrate_score_dib)
mean(transrate_score_ncgr)
sd(transrate_score_dib)
sd(transrate_score_ncgr)
ks.test(transrate_score_dib,transrate_score_ncgr)
# CRBB
CRBB_dib_v_ncgr <- dib_v_ncgr$p_refs_with_CRBB
CRBB_ncgr_v_dib <- ncgr_v_dib$p_refs_with_CRBB
length(CRBB_dib_v_ncgr)
length(CRBB_ncgr_v_dib)
mean(CRBB_dib_v_ncgr)
mean(CRBB_ncgr_v_dib)
sd(CRBB_dib_v_ncgr)
sd(CRBB_ncgr_v_dib)
ks.test(CRBB_dib_v_ncgr,CRBB_ncgr_v_dib)
# ORF content
ORF_dib <- dib_v_ncgr$mean_orf_percent
ORF_ncgr <- ncgr_v_dib$mean_orf_percent
length(ORF_dib)
length(ORF_ncgr)
mean(ORF_dib)
mean(ORF_ncgr)
sd(ORF_dib)
sd(ORF_ncgr)
ks.test(ORF_dib,ORF_ncgr)
# BUSCO content
BUSCO_dib_data <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/busco_scores_MMETSP_protist_trinity2.2.0.csv")
BUSCO_ncgr_data <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/busco_scores_imicrobe_protist.csv")
BUSCO_dib <- BUSCO_dib_data$Complete_BUSCO_perc
BUSCO_ncgr <- BUSCO_ncgr_data$Complete_BUSCO_perc
length(BUSCO_dib)
length(BUSCO_ncgr)
mean(BUSCO_dib)
mean(BUSCO_ncgr)
sd(BUSCO_dib)
sd(BUSCO_ncgr)
ks.test(BUSCO_dib,BUSCO_ncgr)

# taxonomic comparisons
special_flowers = c("MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922")
tax_raw <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/MMETSP_all_evaluation_matrix.csv")
head(tax_raw)
tax_raw <- tax_raw[!tax_raw$SampleName %in% special_flowers,]
phylum_data <-tax_raw[,c(2,34,64,61,49,114,41,45,54)]
phylum <- phylum_data$Phylum
sub_phy<-c("Bacillariophyta","Dinophyta","Ochrophyta","Haptophyta","Ciliophora","Chlorophyta","Cryptophyta")
sub<-phylum_data[phylum_data$Phylum %in% sub_phy,]
fit <- aov(Unique_kmers ~ Phylum,data=sub)

a<-HSD.test(fit,"Phylum",group=TRUE)
#plot

tuk<-glht(fit,linfct=mcp(Phylum="Tukey"))
summary(tuk)
tuk.cld<-cld(tuk)
opar<-par(mai=c(1,1,1.5,1))
plot(tuk.cld)


fit2 <- aov(mean_orf_percent.x ~ Phylum,data=sub)
b<-TukeyHSD(fit2,"Phylum",conf.level=0.95)
tuk<-glht(fit2,linfct=mcp(Phylum="Tukey"))
summary(tuk)
tuk.cld<-cld(tuk)
opar<-par(mai=c(1,1,1.5,1))
plot(tuk.cld)


# PCA
# biological/content:
## ORF
## unique kmers
## p_refs_with_CRBB
## score
# length:
## n_seqs (contigs)
## transrate score
##


# log normalize?
tax_raw <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/MMETSP_all_evaluation_matrix.csv")
special_flowers = c("MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018","MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196","MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922")
tax_raw <- tax_raw[!tax_raw$SampleName %in% special_flowers,]
colnames(tax_raw)
x<-tax_raw[,c(2,34,45,47,48,49,50,51,52,53,60,61,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77:84,86:116,118)]
sub_phy<-c("Bacillariophyta","Dinophyta","Ochrophyta","Haptophyta","Ciliophora","Chlorophyta","Cryptophyta")
sub<-x[x$Phylum %in% sub_phy,]
colnames(sub)
rownames(sub)<-sub$SampleName
sub<-na.omit(sub)
cols=as.integer(sub$Phylum)
x<-sub[,c(3:66)]
x<-as.matrix(x)
head(x)
x_plus<- x + 1
x_log <-log10(x_plus)
dim(x_log)
x_log <- na.omit(x_log)
dim(x_log)
pca = prcomp(x_log)
names = rownames(x)
fac= names


xyplot(
  PC2 ~ PC1, groups=fac, data=as.data.frame(pca$x), pch=16, cex=1.5,
  panel=function(x, y, ...) {
    panel.xyplot(x, y, ...);
  },
  aspect = "fill", col=cols
  #main = draw.key(key = list(rect = list(col = list(col=colours), text = list(levels(fac)), rep = FALSE)))
)
Cols=function(vec){
  cols=rainbow(length(unique(vec)))
  return(cols[as.numeric(as.factor(vec))]) }
par(mfrow=c(1,2))
plot(pca$x[,1:2], col=Cols(as.character(sub$Phylum)), pch=19,
     xlab="Z1",ylab="Z2")
plot(pca$x[,c(1,3)], col=Cols(as.character(sub$Phylum)), pch=19,
     xlab="Z1",ylab="Z3")


## unique gene names in NCGR and DIB
unique_dammit_names <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/unqiue_gene_names_ncgr_dib.csv")
head(unique_dammit_names)
plot(unique_dammit_names$NCGR,unique_dammit_names$DIB,ylim=c(-1,25000),xlim=c(-1,25000))
abline(0,1)

# kmers
dib_ncgr_kmers <- read.csv("~/Documents/UCDavis/dib/MMETSP/git/MMETSP/assembly_evaluation_data/unique_kmers.csv")
head(dib_ncgr_kmers)
plot(dib_ncgr_kmers$Unique_kmers,dib_ncgr_kmers$Unique_kmers_assembly, ylim=c(-1,120000000),xlim=c(-1,120000000))
abline(0,1)

# colors
plot(dib_ncgr_kmers$Unique_kmers,dib_ncgr_kmers$Unique_kmers_assembly,ylim=c(-1,120000000),xlim=c(-1,120000000),col=dib_ncgr_kmers$Phylum)
legend('topleft', pch=c(2,2), col=color, sub_phy, bty='o', cex=.8)
abline(0,1)


