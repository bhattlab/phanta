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
desired_colnames <- c("Taxon", sampnames)

#print(desired_colnames)

# initialize data frame
merged_table <- read.csv(paste0(indir, '/', count_tables[1]), sep='\t', header=FALSE)
colnames(merged_table) <- desired_colnames[1:2]

# loop through files and keep merging
for (i in seq(2,length(count_tables))) {
  f <- paste0(indir, '/', count_tables[i])
  table_to_merge <- read.csv(f, sep='\t', header=FALSE)
  colnames(table_to_merge) <- c("Taxon", desired_colnames[i+1])
  merged_table <- merge(merged_table, table_to_merge, by = c("Taxon"), all=TRUE)
}

# replace NA with 0
merged_table[is.na(merged_table)] <- 0

# make the first column a character vector, not a factor
merged_table[,1] <- as.character(merged_table[,1])

# now output
outpath <- paste0(outdir, '/', 'counts.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')

# Next merge tables normalized out of total Bracken-classified reads

norm_brack_tables_list <- args[4]
norm_brack_tables <- as.character(read.csv(norm_brack_tables_list, header=FALSE)[,1])

# initialize data frame
merged_table <- read.csv(paste0(indir, '/', norm_brack_tables[1]), sep='\t', header=FALSE)
colnames(merged_table) <- desired_colnames[1:2]

# loop through files and keep merging
for (i in seq(2,length(norm_brack_tables))) {
  f <- paste0(indir, '/', norm_brack_tables[i])
  table_to_merge <- read.csv(f, sep='\t', header=FALSE)
  colnames(table_to_merge) <- c("Taxon", desired_colnames[i+1])
  merged_table <- merge(merged_table, table_to_merge, by = c("Taxon"), all=TRUE)
}

# replace NA with 0
merged_table[is.na(merged_table)] <- 0

# make the first column a character vector, not a factor
merged_table[,1] <- as.character(merged_table[,1])

# now output
outpath <- paste0(outdir, '/', 'counts_norm_out_of_bracken_classified.txt')
write.table(merged_table, outpath, quote=FALSE, row.names = FALSE, sep = '\t')
