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
