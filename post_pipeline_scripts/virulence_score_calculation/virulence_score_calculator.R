# Read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
score_map_fpath <- args[1]
comm_abund_fpath <- args[2]
outdir <- args[3]

# Load libraries

library(dplyr)
library(stringr)

# Calculate an overall temperate score for the viral community based on community abundance

# read in table that maps viral species name to temperate score
species_to_temp_score <- read.csv(score_map_fpath,
                                  sep='\t', header=FALSE)
colnames(species_to_temp_score) <- c('species_name', 'temp_score')
# drop the rows that have 'NULL' as the temp_score, then convert to numeric
species_to_temp_score <- filter(species_to_temp_score, temp_score != 'NULL')
species_to_temp_score$temp_score <- as.numeric(species_to_temp_score$temp_score)

# Read in community abundance data frame
community_df <- read.csv(comm_abund_fpath, sep='\t')
# filter down to just Viruses (superkingdom)
viral_species_positions <- grepl('superkingdom_10239', community_df$TaxName, fixed=TRUE)
community_df <- community_df[viral_species_positions,]

# make a version of the TaxName that is just the part after species
just_species_name <- substr(community_df$TaxName, str_locate(community_df$TaxName, 'species_')[,2]+1, nchar(community_df$TaxName))
community_df$species_name <- just_species_name
# filter based on the species we have temperate scores for
community_df <- filter(community_df, species_name %in% species_to_temp_score$species_name)
# drop two columns of community_df
community_df <- select(community_df, -TaxName, -TaxID)
# merge
community_df <- merge(community_df, species_to_temp_score, by='species_name')
rownames(community_df) <- community_df$species_name
community_df <- select(community_df, -species_name)
temp_scores <- community_df$temp_score
community_df <- select(community_df, -temp_score)
# sanity check
if (nrow(community_df) > 1) {
  spec <- rownames(community_df)[2]
  ts <- temp_scores[2]
  stopifnot(ts == species_to_temp_score$temp_score[which(species_to_temp_score$species_name == spec)])
}

# now do element-wise multiplication
community_df_multiplied <- community_df*temp_scores
# sum up the columns
temp_scores_per_sample <- as.data.frame(colSums(community_df_multiplied))
temp_scores_per_sample <- cbind(rownames(temp_scores_per_sample), temp_scores_per_sample)
# rename columns and output to file
colnames(temp_scores_per_sample) <- c('Sample', 'Temperate_Score')
write.table(temp_scores_per_sample,
          paste0(outdir, '/temp_scores_per_sample.txt'), sep='\t', row.names=FALSE, quote=FALSE)
