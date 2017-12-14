#install.packages("klaR",dependencies=TRUE)
#install.packages("spdep",dependencies=TRUE)
#install.packages("AlgDesign",dependencies=TRUE)
#install.packages("agricolae",dependencies=TRUE)
#install.packages("multcomp",dependencies=TRUE)
#install.packages("repr")
library(agricolae)
library(multcomp)
library(repr)
library(RColorBrewer)
setwd("~/Documents/UCDavis/dib/MMETSP")
special_flowers = c("MMETSP0693","MMETSP1019","MMETSP0923","MMETSP0008","MMETSP1002","MMETSP1325","MMETSP1018",
                    "MMETSP1346","MMETSP0088","MMETSP0092","MMETSP0717","MMETSP0223","MMETSP0115","MMETSP0196",
                    "MMETSP0197","MMETSP0398","MMETSP0399","MMETSP0922")
tax_raw <- read.csv("assembly_evaluation_data/MMETSP_all_evaluation_matrix.csv")
#head(tax_raw)
colors=palette(brewer.pal(n=7,name="Dark2"))

tax_raw <- tax_raw[!tax_raw$SampleName %in% special_flowers,]
phylum_data <-tax_raw[,c(2,34,64,61,49,114,41,45,54)]
phylum <- phylum_data$Phylum
# Restrict data to top 7 most common Phyla
sub_phy<-c("Bacillariophyta","Dinophyta","Ochrophyta","Haptophyta","Ciliophora","Chlorophyta","Cryptophyta")
sub<-phylum_data[phylum_data$Phylum %in% sub_phy,]
fit <- aov(Unique_kmers ~ Phylum,data=sub)
a<-HSD.test(fit,"Phylum",group=TRUE)
tuk<-glht(fit,linfct=mcp(Phylum="Tukey"))
summary(tuk)
tuk.cld<-cld(tuk)
opar<-par(mai=c(1,1,1.5,1))
options(repr.plot.width=12, repr.plot.height=10)
pdf("paper/Figure8_tukey_taxa_unique_kmers.pdf")
plot(tuk.cld,col=colors,ylab="Mean %ORF")
dev.off()
plot(tuk.cld,col=colors)
fit2 <- aov(mean_orf_percent.x ~ Phylum,data=sub)
b<-TukeyHSD(fit2,"Phylum",conf.level=0.95)
tuk<-glht(fit2,linfct=mcp(Phylum="Tukey"))
summary(tuk)
tuk.cld<-cld(tuk)
opar<-par(mai=c(1,1,1.5,1))
options(repr.plot.width=12, repr.plot.height=10)
pdf("paper/Figure8_tukey_taxa_mean_orf.pdf")
plot(tuk.cld,col=colors)
dev.off()
plot(tuk.cld,col=colors, ylab="Unique k-mers")


