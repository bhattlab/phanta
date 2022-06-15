library(stringr)

# need to read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
outdir <- args[1]

scaled_reports_list <- args[2]
scaled_reports <- as.character(read.csv(scaled_reports_list, header=FALSE)[,1])

# figure out what column names we'll want for the merged data frame
# find locations of '.' in the file names
locations <- str_locate(scaled_reports, '\\.')[,1]
sampnames <- substr(scaled_reports, 1, locations-1)
desired_colnames <- c("TaxID", sampnames)

# initialize data frame
merged_table <- read.csv(paste0(outdir, '/', scaled_reports[1]), sep='\t', header=TRUE)
taxid_col <- which(colnames(merged_table) == 'taxonomy_id')
community_col <- which(colnames(merged_table) == 'community_abundance')
merged_table <- merged_table[,c(taxid_col, community_col)]
colnames(merged_table) <- desired_colnames[1:2]

# loop through files and keep merging
if (length(scaled_reports) > 1) {
for (i in seq(2,length(scaled_reports))) {
  f <- paste0(outdir, '/', scaled_reports[i])
  table_to_merge <- read.csv(f, sep='\t', header=TRUE)
  taxid_col <- which(colnames(table_to_merge) == 'taxonomy_id')
  community_col <- which(colnames(table_to_merge) == 'community_abundance')
  table_to_merge <- table_to_merge[,c(taxid_col, community_col)]
  colnames(table_to_merge) <- c("TaxID", desired_colnames[i+1])
  merged_table <- merge(merged_table, table_to_merge, by = c("TaxID"), all=TRUE)
}}

# replace NA with 0
merged_table[is.na(merged_table)] <- 0

# make the first column a character vector, not a factor
merged_table[,1] <- as.character(merged_table[,1])

# now output
outpath <- paste0(outdir, '/', 'corrected_relative_abundance_temp.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')
