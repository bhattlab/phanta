library(stringr)

# need to read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
outdir <- args[1]

scaled_reports_list <- args[2]
scaled_reports <- as.character(read.csv(scaled_reports_list, header=FALSE)[,1])

# figure out what column names we'll want for the merged data frame
# find locations of '.' in the file names
locations <- str_locate(scaled_reports, '\\.krak.report')[,1]
sampnames <- substr(scaled_reports, 1, locations-1)
desired_colnames <- c("TaxID", sampnames)

# also figure out which samples failed
failed <- args[3]
failed_samples <- tryCatch(
  expr = {
    as.character(read.csv(failed, header=FALSE)[,1])
  },
  error = function(e){
    return(c())
  })

# initialize data frame
sample <- desired_colnames[2]
if (sample %in% failed_samples) {
  merged_table <- data.frame(matrix(ncol = 1, nrow = 0))
  colnames(merged_table) <- desired_colnames[1]
} else {
  merged_table <- read.csv(paste0(outdir, '/', scaled_reports[1]), sep='\t', header=TRUE)
  taxid_col <- which(colnames(merged_table) == 'taxonomy_id')
  rel_taxon_col <- which(colnames(merged_table) == 'rel_taxon_abundance')
  merged_table <- merged_table[,c(taxid_col, rel_taxon_col)]
  colnames(merged_table) <- desired_colnames[1:2]
}

# loop through files and keep merging
if (length(scaled_reports) > 1) {
for (i in seq(2,length(scaled_reports))) {
  sample <- desired_colnames[i+1]
  if (sample %in% failed_samples) {
  } else {
  f <- paste0(outdir, '/', scaled_reports[i])
  table_to_merge <- read.csv(f, sep='\t', header=TRUE)
  taxid_col <- which(colnames(table_to_merge) == 'taxonomy_id')
  rel_taxon_col <- which(colnames(table_to_merge) == 'rel_taxon_abundance')
  table_to_merge <- table_to_merge[,c(taxid_col, rel_taxon_col)]
  colnames(table_to_merge) <- c("TaxID", sample)
  merged_table <- merge(merged_table, table_to_merge, by = c("TaxID"), all=TRUE)
  # replace NA with 0
  merged_table[is.na(merged_table)] <- 0
  }}}

for (sample in failed_samples) {
  merged_table[[sample]] <- rep(NA, nrow(merged_table))
}

# make the first column a character vector, not a factor
merged_table[,1] <- as.character(merged_table[,1])

# now output
outpath <- paste0(outdir, '/', 'relative_taxonomic_abundance_temp.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')
