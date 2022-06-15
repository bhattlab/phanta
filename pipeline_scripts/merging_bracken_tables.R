library(stringr)

# need to read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
indir <- args[1]
outdir <- args[2]

# First merge counts tables

counts_tables_list <- args[3]
count_tables <- as.character(read.csv(counts_tables_list, header=FALSE)[,1])

#print(count_tables)

# figure out what column names we'll want for the merged data frame
# find locations of '.' in the file names
locations <- str_locate(count_tables, '\\.')[,1]
sampnames <- substr(count_tables, 1, locations-1)
desired_colnames <- c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs", sampnames)

#print(desired_colnames)

# initialize data frame
merged_table <- read.csv(paste0(indir, '/', count_tables[1]), sep='\t', header=FALSE)
colnames(merged_table) <- desired_colnames[1:3]

# loop through files and keep merging
if (length(count_tables) > 1) {
for (i in seq(2,length(count_tables))) {
  f <- paste0(indir, '/', count_tables[i])
  table_to_merge <- read.csv(f, sep='\t', header=FALSE)
  colnames(table_to_merge) <- c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs", desired_colnames[i+2])
  merged_table <- merge(merged_table, table_to_merge, by = c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs"), all=TRUE)
}}

# replace NA with 0
merged_table[is.na(merged_table)] <- 0

# make the first two columns character vectors, not factors
merged_table[,1] <- as.character(merged_table[,1])
merged_table[,2] <- as.character(merged_table[,2])

# now output
outpath <- paste0(outdir, '/', 'counts.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')

# Next merge tables normalized out of total Bracken-classified reads

norm_brack_tables_list <- args[4]
norm_brack_tables <- as.character(read.csv(norm_brack_tables_list, header=FALSE)[,1])

# the samples should be in the same order - do a sanity check
locations <- str_locate(norm_brack_tables, '\\.')[,1]
sampnames <- substr(norm_brack_tables, 1, locations-1)
desired_colnames_test <- c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs", sampnames)
stopifnot(desired_colnames == desired_colnames_test)

# initialize data frame
merged_table <- read.csv(paste0(indir, '/', norm_brack_tables[1]), sep='\t', header=FALSE)
colnames(merged_table) <- desired_colnames[1:3]

# loop through files and keep merging
if (length(norm_brack_tables) > 1) {
for (i in seq(2,length(norm_brack_tables))) {
  f <- paste0(indir, '/', norm_brack_tables[i])
  table_to_merge <- read.csv(f, sep='\t', header=FALSE)
  colnames(table_to_merge) <- c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs", desired_colnames[i+2])
  merged_table <- merge(merged_table, table_to_merge, by = c("Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs"), all=TRUE)
}}

# replace NA with 0
merged_table[is.na(merged_table)] <- 0

# make the first two columns character vectors, not factors
merged_table[,1] <- as.character(merged_table[,1])
merged_table[,2] <- as.character(merged_table[,2])

# now output
outpath <- paste0(outdir, '/', 'relative_abundance.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')
