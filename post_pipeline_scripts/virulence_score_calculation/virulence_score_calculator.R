# Read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
score_map_fpath <- args[1]
abundance_fpath <- args[2]
outdir <- args[3]

# Load libraries

library(dplyr)
library(stringr)

# Calculate an overall virulence score for the viral community based on corrected relative abundance

# read in table that maps viral species name to virulence score
species_to_vir_score <- read.csv(score_map_fpath,
                                  sep='\t', header=FALSE)
colnames(species_to_vir_score) <- c('species_name', 'vir_score')
# drop the rows that have 'NULL' as the vir_score, then convert to numeric
species_to_vir_score <- filter(species_to_vir_score, vir_score != 'NULL')
species_to_vir_score$vir_score <- as.numeric(species_to_vir_score$vir_score)

# Read in abundance data frame
abundance_df <- read.csv(abundance_fpath, sep='\t')
# filter down to just Viruses (superkingdom)
viral_species_positions <- grepl('superkingdom_10239', abundance_df$TaxName, fixed=TRUE)
abundance_df <- abundance_df[viral_species_positions,]

# make a version of the TaxName that is just the part after species
just_species_name <- substr(abundance_df$TaxName, str_locate(abundance_df$TaxName, 'species_')[,2]+1, nchar(abundance_df$TaxName))
abundance_df$species_name <- just_species_name
# filter based on the species we have scores for
abundance_df <- filter(abundance_df, species_name %in% species_to_vir_score$species_name)
# drop two unnecessary columns
abundance_df <- select(abundance_df, -TaxName, -TaxID)
# merge
abundance_df <- merge(abundance_df, species_to_vir_score, by='species_name')
rownames(abundance_df) <- abundance_df$species_name
abundance_df <- select(abundance_df, -species_name)
vir_scores <- abundance_df$vir_score
abundance_df <- select(abundance_df, -vir_score)
# sanity check
if (nrow(abundance_df) > 1) {
  spec <- rownames(abundance_df)[2]
  vs <- vir_scores[2]
  stopifnot(vs == species_to_vir_score$vir_score[which(species_to_vir_score$species_name == spec)])
}

# now do element-wise multiplication
abundance_df_multiplied <- abundance_df*vir_scores
# sum up the columns
vir_scores_per_sample <- as.data.frame(colSums(abundance_df_multiplied))
vir_scores_per_sample <- cbind(rownames(vir_scores_per_sample), vir_scores_per_sample)
# rename columns and output to file
colnames(vir_scores_per_sample) <- c('Sample', 'Virulence_Score')
write.table(vir_scores_per_sample,
          paste0(outdir, '/virulence_scores_per_sample.txt'), sep='\t', row.names=FALSE, quote=FALSE)
