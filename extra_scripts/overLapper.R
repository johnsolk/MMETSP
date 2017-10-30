##########################################
## Intersect and Venn Diagram Functions ##
##########################################
## Author: Thomas Girke
## Last update: August 15, 2009
## Utilities: 
## (1) Venn Intersects
##     Computation of Venn intersects among 2-20 or more sample sets using the typical
##     'only in' intersect logic of Venn comparisons, such as: objects present only in 
##     set A, objects present only in the intersect of A & B, etc. Due to this restrictive 
##     intersect logic, the combined Venn sets contain no duplicates.  
## (2) Regular Intersects
##     Computation of regular intersects among 2-20 or more sample sets using the
##     following intersect logic: objects present in the intersect of A & B, objects present 
##     in the intersect of A & B & C, etc. The approach results usually in many duplications 
##     of objects among the intersect sets.
## (3) Graphical Utilities
##     - Venn diagrams of 2-5 sample sets. 
##     - Bar plots for the results of Venn intersect and all intersect approaches derived 
##       from many samples sets. 
##
## Detailed instructions for using the functions of this script are available on this page:
##     http://faculty.ucr.edu/~tgirke/Documents/R_BioCond/R_BioCondManual.html#R_graphics_venn

#######################################
## Define Generic Intersect Function ##
#######################################
## Computation of (1) Venn Intersects and (2) Regular Intersects
overLapper <- function(setlist=setlist, complexity=1:length(setlist), sep="-", cleanup=FALSE, keepdups=FALSE, type) {
	## Clean up of sample sets to minimize formatting issues 
	if(cleanup==TRUE) {
		## Set all characters to upper case 
		setlist <- sapply(setlist, function(x) gsub("([A-Z])", "\\U\\1", x, perl=T, ignore.case=T))
		## Remove leading and trailing spaces
		setlist <- sapply(setlist, function(x) gsub("^ {1,}| {1,}$", "", x, perl=T, ignore.case=T))
	}
	
	## Append object counter to retain duplicates 
	if(keepdups==TRUE) {
		dupCount <- function(setlist=setlist) {
			count <- table(setlist)
			paste(rep(names(count), count), unlist(sapply(count, function(x) seq(1, x))), sep=".")
		}
		mynames <- names(setlist)
		setlist <- lapply(setlist, function(x) dupCount(x)) # lapply necessary for numeric data!
		names(setlist) <- mynames
	}	

	## Create intersect matrix (removes duplicates!)
	setunion <- sort(unique(unlist(setlist)))
	setmatrix <- sapply(names(setlist), function(x) setunion %in% unique(setlist[[x]])) 
	rownames(setmatrix) <- setunion
	storage.mode(setmatrix) <- "numeric"

	## Create all possible sample combinations within requested complexity levels
	labels <- names(setlist)
	allcombl <- lapply(complexity, function(x) combn(labels, m=x, simplify=FALSE))
	allcombl <- unlist(allcombl, recursive=FALSE)
	complevels <- sapply(allcombl, length)
	
	## Return intersect list for generated sample combinations 
	if(type=="intersects") {
		OLlist <- sapply(seq(along=allcombl), function(x) setunion[rowSums(setmatrix[, rep(allcombl[[x]], 2)]) == 2 * length(allcombl[[x]])])
		names(OLlist) <- sapply(allcombl, paste, collapse=sep)
		return(list(Set_List=setlist, Intersect_Matrix=setmatrix, Complexity_Levels=complevels, Intersect_List=OLlist))
	}	

	## Return Venn intersect list for generated sample combinations 
	if(type=="vennsets") {
		vennSets <- function(setmatrix=setmatrix, allcombl=allcombl, index=1) {
			mycol1 <- which(colnames(setmatrix) %in% allcombl[[index]])
			mycol2 <- which(!colnames(setmatrix) %in% allcombl[[index]])
			cond1 <- rowSums(setmatrix[, rep(mycol1, 2)]) == 2 * length(mycol1)
			cond2 <- rowSums(setmatrix[, rep(mycol2, 2)]) == 0
			return(setunion[cond1 & cond2])
		}
		vennOLlist <- sapply(seq(along=allcombl), function(x) vennSets(setmatrix=setmatrix, allcombl=allcombl, index=x))
		names(vennOLlist) <- sapply(allcombl, paste, collapse=sep)
		return(list(Set_List=setlist, Intersect_Matrix=setmatrix, Complexity_Levels=complevels, Venn_List=vennOLlist))
	}
}

###########################################
## Define Venn Diagram Plotting Function ##
###########################################
vennPlot <- function(counts=counts, mymain="Venn Diagram", mysub="default", setlabels="default", yoffset=seq(0,10,by=0.34), ccol=rep(1,31), lcol=c("#FF0000", "#008B00", "#0000FF", "#FF00FF", "#CD8500"), lines=c("#FF0000", "#008B00", "#0000FF", "#FF00FF", "#CD8500"), mylwd=3, diacol=1, type="ellipse", ccex=1.0, lcex=1.0, ...) {
	## Enforce list structure to support multiple venn sets 
	if(is.list(counts)==FALSE) {
		counts <- list(counts)
	}
	
	## Check for supported number of Venn counts: 3, 7, 15 and 31
	if(!length(counts[[1]]) %in%  c(3,7,15,31)) stop("Only the counts from 2-5 way venn comparisons are supported.")
	
	## 2-way Venn diagram
	if(length(counts[[1]])==3) {
		## Define subtitle
		if(mysub=="default") {
			sample_counts <- sapply(names(counts[[1]])[1:2], function(x) sum(counts[[1]][grep(x, names(counts[[1]]))]))
			mysub <- paste(paste("Unique objects: All =", sum(counts[[1]])), paste("; S1 =", sample_counts[1]), paste("; S2 =", sample_counts[2]), sep="")
		} else { 
			mysub <- mysub 
		}
		
		## Plot venn shapes
		symbols(x=c(4, 6), y = c(6, 6), circles=c(2, 2), xlim=c(0, 10), ylim=c(0, 10), inches=F, main=mymain, sub=mysub, lwd=mylwd, xlab="", ylab="",  xaxt="n", yaxt="n", bty="n", fg=lines, ...); 
		
		## Add counts
		for(i in seq(along=counts)) {
			olDF <- data.frame(x=c(3.1, 7.0, 5.0), 
                                           y=c(6.0, 6.0, 6.0), 
                                           counts=counts[[i]])
			text(olDF$x, olDF$y + yoffset[i], olDF$counts, col=ccol, cex=ccex, ...)
		}
                
		## Add sample labels
		if(length(setlabels)==1 & setlabels[1]=="default") { 
			setlabels <- names(counts[[1]][1:2])
		} else {
			setlabels <- setlabels
		}
		text(c(2.0, 8.0), c(8.8, 8.8), labels=setlabels, col=lcol, cex=lcex, ...)	
	}
 
	## 3-way Venn diagram
	if(length(counts[[1]])==7) { 
		## Define subtitle
		if(mysub=="default") {
			sample_counts <- sapply(names(counts[[1]])[1:3], function(x) sum(counts[[1]][grep(x, names(counts[[1]]))]))
			mysub <- paste(paste("Unique objects: All =", sum(counts[[1]])), paste("; S1 =", sample_counts[1]), paste("; S2 =", sample_counts[2]), paste("; S3 =", sample_counts[3]), sep="")
		} else { 
			mysub <- mysub
		}
		
		## Plot venn shapes
		symbols(x=c(4, 6, 5), y=c(6, 6, 4), circles=c(2, 2, 2), xlim=c(0, 10), ylim=c(0, 10), inches=FALSE, main=mymain, sub=mysub, lwd=mylwd, xlab="", ylab="", xaxt="n", yaxt="n", bty="n", fg=lines, ...)
		
		## Add counts
		for(i in seq(along=counts)) {
			olDF <- data.frame(x=c(3.0, 7.0, 5.0, 5.0, 3.8, 6.3, 5.0), 
                                           y=c(6.5, 6.5, 3.0, 7.0, 4.6, 4.6, 5.3), 
                                           counts=counts[[i]])
	        	text(olDF$x, olDF$y + yoffset[i], olDF$counts, col=ccol, cex=ccex, ...)

		}

                ## Add sample labels
		if(length(setlabels)==1 & setlabels[1]=="default") { 
			setlabels <- names(counts[[1]][1:3])
		} else {
			setlabels <- setlabels
		}
		text(c(2.0, 8.0, 6.0), c(8.8, 8.8, 1.1), labels=setlabels, col=lcol, cex=lcex, ...)	
	}
	
	## 4-way Venn diagram with ellipses
	if(length(counts[[1]])==15 & type=="ellipse") {
		## Define subtitle
		if(mysub=="default") {
			sample_counts <- sapply(names(counts[[1]])[1:4], function(x) sum(counts[[1]][grep(x, names(counts[[1]]))]))
			mysub <- paste(paste("Unique objects: All =", sum(counts[[1]])), paste("; S1 =", sample_counts[1]), paste("; S2 =", sample_counts[2]), paste("; S3 =", sample_counts[3]), paste("; S4 =", sample_counts[4]), sep="")
		} else { 
			mysub <- mysub
		}
		
		## Plot ellipse
		plotellipse <- function (center=c(1,1), radius=c(1,2), rotate=1, segments=360, xlab="", ylab="", ...) {
			angles <- (0:segments) * 2 * pi/segments  
			rotate <- rotate*pi/180
			ellipse <- cbind(radius[1] * cos(angles), radius[2] * sin(angles))
			ellipse <- cbind( ellipse[,1]*cos(rotate) + ellipse[,2]*sin(rotate), ellipse[,2]*cos(rotate) - ellipse[,1]*sin(rotate) )
			ellipse <- cbind(center[1]+ellipse[,1], center[2]+ellipse[,2])	
			plot(ellipse, type = "l", xlim = c(0, 10), ylim = c(0, 10), xlab = "", ylab = "", ...)
		}
		## Plot ellipse as 4-way venn diagram
		ellipseVenn <- function(...) {
			split.screen(c(1,1))
			plotellipse(center=c(3.5,3.6), radius=c(2,4), rotate=-35, segments=360, xlab="", ylab="", col=lines[1], axes=FALSE, main=mymain, sub=mysub, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(4.7,4.4), radius=c(2,4), rotate=-35, segments=360, xlab="", ylab="", col=lines[2], axes=FALSE, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(5.3,4.4), radius=c(2,4), rotate=35, segments=360, xlab="", ylab="", col=lines[3], axes=FALSE, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(6.5,3.6), radius=c(2,4), rotate=35, segments=360, xlab="", ylab="", col=lines[4], axes=FALSE, lwd=mylwd, ...)
			## Add counts
			for(i in seq(along=counts)) {
				olDF <- data.frame(x=c(1.5, 3.5, 6.5, 8.5, 2.9, 3.1, 5.0, 5.0, 6.9, 7.1, 3.6, 5.8, 4.2, 6.4, 5.0), 
                                                   y=c(4.8, 7.2, 7.2, 4.8, 5.9, 2.2, 0.7, 6.0, 2.2, 5.9, 4.0, 1.4, 1.4, 4.0, 2.8), 
                                                   counts=counts[[i]])
				text(olDF$x, olDF$y + yoffset[i], olDF$counts, col=ccol, cex=ccex, ...)
			}
			## Add sample labels
			if(length(setlabels)==1 & setlabels[1]=="default") { 
				setlabels <- names(counts[[1]][1:4])
			} else {
				setlabels <- setlabels
			}
			text(c(0.4, 2.8, 7.5, 9.4), c(7.3, 8.3, 8.3, 7.3), labels=setlabels, col=lcol, cex=lcex, ...)
			close.screen(all=TRUE) 
		}
		ellipseVenn(...)
	} 

	## 4-way Venn diagram with circles (pseudo-venn diagram that misses two overlap sectors) 
	if(length(counts[[1]])==15 & type=="circle") {
		## Define subtitle
		if(mysub=="default") {
			sample_counts <- sapply(names(counts[[1]])[1:4], function(x) sum(counts[[1]][grep(x, names(counts[[1]]))]))
			mysub <- paste(paste("Unique objects: All =", sum(counts[[1]])), paste("; S1 =", sample_counts[1]), paste("; S2 =", sample_counts[2]), paste("; S3 =", sample_counts[3]), paste("; S4 =", sample_counts[4]), sep="")
		} else { 
			mysub <- mysub
		}
		
		## Plot venn shapes
		symbols(x=c(4, 5.5, 4, 5.5), y = c(6, 6, 4.5, 4.5), circles=c(2, 2, 2, 2), xlim=c(0, 10), ylim=c(0, 10), inches=FALSE, main=mymain, sub=mysub, lwd=mylwd, xlab="", ylab="", xaxt="n", yaxt="n", bty="n", fg=lines, ...)
		
		## Add counts
		for(i in seq(along=counts)) {
		        olDF <- data.frame(x=c(3.0, 6.5, 3.0, 6.5, 4.8, 3.0, 4.8, 4.8, 6.5, 4.8, 3.9, 5.7, 3.9, 5.7, 4.8), 
                                           y=c(7.2, 7.2, 3.2, 3.2, 7.2, 5.2, 0.4, 0.4, 5.2, 3.2, 6.3, 6.3, 4.2, 4.2, 5.2), 
                                           counts=counts[[i]])
			text(olDF$x[-c(7,8)], olDF$y[-c(7,8)] + yoffset[i], olDF$counts[-c(7,8)], col=ccol, cex=ccex, ...) # rows 14-15 of olDF are printed in next step
			text(c(4.8), c(0.8) + yoffset[i], paste("Only in ", names(counts[[1]][1]), " & ", names(counts[[1]][4]), ": ", olDF$counts[7], "; Only in ", names(counts[[1]][2]), " & ", names(counts[[1]][3]), ": ", olDF$counts[8], sep=""), col=diacol, cex=ccex, ...)
		}

                ## Add sample labels
			if(length(setlabels)==1 & setlabels[1]=="default") { 
				setlabels <- names(counts[[1]][1:4])
			} else {
				setlabels <- setlabels
			}
		text(c(2.0, 7.5, 2.0, 7.5), c(8.3, 8.3, 2.0, 2.0), labels=setlabels, col=lcol, cex=lcex, ...)
	} 
	
	## 5-way Venn diagram
	if(length(counts[[1]])==31) {
		## Define subtitle
		if(mysub=="default") {
			sample_counts <- sapply(names(counts[[1]])[1:5], function(x) sum(counts[[1]][grep(x, names(counts[[1]]))]))
			mysub <- paste(paste("Unique objects: All =", sum(counts[[1]])), paste("; S1 =", sample_counts[1]), paste("; S2 =", sample_counts[2]), paste("; S3 =", sample_counts[3]), paste("; S4 =", sample_counts[4]), paste("; S5 =", sample_counts[5]), sep="")
		} else { 
			mysub <- mysub
		}
		
		## Plot ellipse
		plotellipse <- function (center=c(1,1), radius=c(1,2), rotate=1, segments=360, xlab="", ylab="", ...) {
			angles <- (0:segments) * 2 * pi/segments  
			rotate <- rotate*pi/180
			ellipse <- cbind(radius[1] * cos(angles), radius[2] * sin(angles))
			ellipse <- cbind( ellipse[,1]*cos(rotate) + ellipse[,2]*sin(rotate), ellipse[,2]*cos(rotate) - ellipse[,1]*sin(rotate) )
			ellipse <- cbind(center[1]+ellipse[,1], center[2]+ellipse[,2])	
			plot(ellipse, type = "l", xlim = c(0, 10), ylim = c(0, 10), xlab = "", ylab = "", ...)
		}
		## Plot ellipse as 5-way venn diagram
		ellipseVenn <- function(...) {
			split.screen(c(1,1))
			screen(1, new=FALSE)
			plotellipse(center=c(4.83,6.2), radius=c(1.43,4.11), rotate=0, segments=360, xlab="", ylab="", col=lines[1], axes=FALSE, main=mymain, sub=mysub, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(6.25,5.4), radius=c(1.7,3.6), rotate=66, segments=360, xlab="", ylab="", col=lines[2], axes=FALSE, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(6.1,3.5), radius=c(1.55,3.9), rotate=150, segments=360, xlab="", ylab="", col=lines[3], axes=FALSE, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(4.48,3.15), radius=c(1.55,3.92), rotate=210, segments=360, xlab="", ylab="", col=lines[4], axes=FALSE, lwd=mylwd, ...)
			screen(1, new=FALSE)
			plotellipse(center=c(3.7,4.8), radius=c(1.7,3.6), rotate=293.5, segments=360, xlab="", ylab="", col=lines[5], axes=FALSE, lwd=mylwd, ...)

			## Add counts
			for(i in seq(along=counts)) {
				olDF <- data.frame(x=c(4.85, 8.0, 7.1, 3.5, 2.0, 5.90, 4.4, 4.60, 3.60, 7.1, 6.5, 3.2, 5.4, 6.65, 3.40, 5.00, 6.02, 3.60, 5.20, 4.03, 4.20, 6.45, 6.8, 3.39, 6.03, 5.74, 4.15, 3.95, 5.2, 6.40, 5.1), 
                                                   y=c(8.30, 6.2, 1.9, 1.6, 5.4, 6.85, 6.6, 2.45, 6.40, 4.3, 6.0, 4.6, 2.1, 3.40, 3.25, 6.43, 6.38, 5.10, 2.49, 6.25, 3.08, 5.30, 4.0, 3.80, 3.20, 5.95, 5.75, 3.75, 3.0, 4.50, 4.6),
					counts=counts[[i]]) 
				text(olDF$x, olDF$y + yoffset[i], olDF$counts, col=ccol, cex=ccex, ...)
			}
			## Add sample labels
			if(length(setlabels)==1 & setlabels[1]=="default") { 
				setlabels <- names(counts[[1]][1:5])
			} else {
				setlabels <- setlabels
			}
			text(c(5.7, 7.9, 8.5, 4.2, 0.8), c(9.9, 7.9, 1.9, 0.0, 7.3), adj=c(0, 0.5), labels=setlabels, col=lcol, cex=lcex, ...)
			close.screen(all=TRUE) 
		}
		ellipseVenn(...)
	} 
}

##############################
## Define Bar Plot Function ##
##############################
## Plots the counts of Venn/regular intersects generated by the overLapper function
olBarplot <- function(OLlist=OLlist, mycol="default", margins=c(6, 10, 3, 2), mincount=0, mysub="default", ...) {
	## Generate counts and allow lower limit 
	counts <- sapply(OLlist[[4]], length)
	mylogical <- counts >= mincount
	counts <- counts[mylogical]
	
	## Color bars by default by complexity levels 
	if(mycol=="default") {
		mycol <- OLlist$Complexity_Levels
		mycol <- mycol[mylogical] 
	} else {
		mycol <- mycol	
	}

	## Define subtitle
	if(mysub=="default") {
		mysub <- paste("Min Count:", mincount)
	} else {
		mysub <- mysub
	}
	
	## Generate bar plot with defined margins
	par(mar=margins) # Define margins to allow long labels
	barplot(counts, col=mycol, sub=mysub, ...)
	par(mar=c(5, 4, 4, 2) + 0.1) # Set margins back to default
}




