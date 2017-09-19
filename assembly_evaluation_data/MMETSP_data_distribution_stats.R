require(graphics)
x <- rnorm(50)
y <- runif(30)
# Do x and y come from the same distribution?
ks.test(x, y)
# Does x come from a shifted gamma distribution with shape 3 and rate 2?
ks.test(x+2, "pgamma", 3, 2) # two-sided, exact
ks.test(x+2, "pgamma", 3, 2, exact = FALSE)
ks.test(x+2, "pgamma", 3, 2, alternative = "gr")

# test if x is stochastically larger than x2
x2 <- rnorm(50, -1)
plot(ecdf(x), xlim = range(c(x, x2)))
plot(ecdf(x2), add = TRUE, lty = "dashed")
t.test(x, x2, alternative = "g")
wilcox.test(x, x2, alternative = "g")
ks.test(x, x2, alternative = "l")

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