# Read in arguments from command line
args <- commandArgs(trailingOnly=TRUE)
virulence_threshold <- as.numeric(args[1])
score_map_fpath <- args[2]
counts_fpath <- args[3]
rel_abund_fpath <- args[4]
out_fname <- args[5]

# Load libraries

library(dplyr)
library(stringr)

# First determine the total number of viral reads per sample
counts <- read.csv(counts_fpath, sep='\t', header=TRUE)
# filter down to just Viruses (superkingdom)
viral_species_positions <- grepl('superkingdom_Viruses', counts$Taxon_Lineage_with_Names, fixed=TRUE)
counts <- counts[viral_species_positions,]
viral_counts <- as.data.frame(colSums(select(counts, -Taxon_Lineage_with_Names, -Taxon_Lineage_with_IDs)))

# write a function to make such a one-column DF mergeable by sample name
# will need this a lot below
make_mergeable <- function(one_col_df, desired_colname) {
  for_merge <- cbind(rownames(one_col_df), one_col_df[,1])
  colnames(for_merge) <- c('sample', desired_colname)
  return(for_merge)
}

merged <- make_mergeable(viral_counts, 'tot_viral_reads')

# Next goal is to determine the relative presence/absence of virulent and temperate phages in each sample

# First, read in the score map
species_to_vir_score <- read.csv(score_map_fpath,
                                  sep='\t', header=FALSE)
colnames(species_to_vir_score) <- c('species_name', 'vir_score')
# drop the rows that have 'NULL' as the vir_score, then convert to numeric
species_to_vir_score <- filter(species_to_vir_score, vir_score != 'NULL')
species_to_vir_score$vir_score <- as.numeric(species_to_vir_score$vir_score)
# make a vector of virulent phages and a vector of temperate phages
virulent_phages <- species_to_vir_score$species_name[which(species_to_vir_score$vir_score > virulence_threshold)]
temperate_phages <- species_to_vir_score$species_name[which(species_to_vir_score$vir_score <= virulence_threshold)]

# Next, read in the relative abundance data frame
rel_abund <- read.csv(rel_abund_fpath, sep='\t')
# filter down to just Viruses (superkingdom)
viral_species_positions <- grepl('superkingdom_Viruses', rel_abund$Taxon_Lineage_with_Names, fixed=TRUE)
rel_abund <- rel_abund[viral_species_positions,]

# make a version of the Taxon_Lineage_with_Names that is just the part after species
rel_abund$species_name <- substr(rel_abund$Taxon_Lineage_with_Names, str_locate(rel_abund$Taxon_Lineage_with_Names, 'species_')[,2]+1, nchar(rel_abund$Taxon_Lineage_with_Names))
# drop two unnecessary columns
rel_abund <- select(rel_abund, -Taxon_Lineage_with_IDs, -Taxon_Lineage_with_Names)
# figure out the lifestyle of each of the species in the DF
rel_abund$lifestyle <- ifelse(rel_abund$species_name %in% virulent_phages, 'Virulent',
                              ifelse(rel_abund$species_name %in% temperate_phages, 'Temperate', 'Unknown'))
# break the DF into virulent, temperate, unknown
# then drop the unnecessary columns
virulent <- select(filter(rel_abund, lifestyle == 'Virulent'), -species_name, -lifestyle)
temperate <- select(filter(rel_abund, lifestyle == 'Temperate'), -species_name, -lifestyle)
unknown <- select(filter(rel_abund, lifestyle == 'Unknown'), -species_name, -lifestyle)

num_virulent_phages <- make_mergeable(data.frame(colSums(virulent > 0)), 'num_virulent_phages')
num_temperate_phages <- make_mergeable(data.frame(colSums(temperate > 0)), 'num_temperate_phages')
num_unknown_phages <- make_mergeable(data.frame(colSums(unknown > 0)), 'num_unknown_phages')

# merge each of them!
merged <- merge(merged, num_virulent_phages, by='sample')
merged <- merge(merged, num_temperate_phages, by='sample')
merged <- merge(merged, num_unknown_phages, by='sample')

# now tack on the total abundance of the virulent and temperate phages
virulent_phages_abundance <- make_mergeable(data.frame(colSums(virulent)), 'virulent_phages_abundance')
temperate_phages_abundance <- make_mergeable(data.frame(colSums(temperate)), 'temperate_phages_abundance')

merged <- merge(merged, virulent_phages_abundance, by='sample')
merged <- merge(merged, temperate_phages_abundance, by='sample')

# finally calculate two ratios
# virulent to temperate phages presence
merged$ratio_num_virulent_temperate <- as.numeric(merged$num_virulent_phages)/as.numeric(merged$num_temperate_phages)
# virulent to temperate phages abundance 
merged$ratio_abund_virulent_temperate <- as.numeric(merged$virulent_phages_abundance)/as.numeric(merged$temperate_phages_abundance)

write.table(merged, out_fname, sep='\t', quote=FALSE, row.names=FALSE)
