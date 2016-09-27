imicrobe<-read.csv("imicrobe/Callum_FINAL_biosample_ids.csv")
ncbi<-read.csv("SraRunInfo.csv")
MMETSP_id_NCBI<-ncbi$SampleName
MMETSP_id_imicrobe<-imicrobe$SAMPLE_NAME
source('~/Documents/scripts/overLapper.R')
setlist <- list(NCBI=as.vector(MMETSP_id_NCBI),imicrobe=as.vector(MMETSP_id_imicrobe))
OLlist <- overLapper(setlist=setlist, sep="", type="vennsets")
counts <- sapply(OLlist$Venn_List, length)
vennPlot(counts=counts)
overlap<-intersect(MMETSP_id_NCBI,MMETSP_id_imicrobe)
length(overlap)
OLlist$Venn_List$NCBI
OLlist$Venn_List$imicrobe
length(unique(MMETSP_id_NCBI))
length(unique(ncbi$Run))
length(unique(MMETSP_id_imicrobe))
ncbi_719<-read.csv("~/Downloads/SraRunInfo_719.csv")
length(unique(ncbi_719$Run))
length(unique(ncbi_719$SampleName))
extra<-ncbi_719$Run[!(ncbi_719$Run %in% ncbi$Run)]
ncbi_sra_duplicated_MMETSP<-ncbi[duplicated(ncbi$SampleName),]

