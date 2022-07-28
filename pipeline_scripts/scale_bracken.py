import pandas as pd
import sys

def main():
    ###step 1- input
    kraken_db = sys.argv[1]
    bracken_report = sys.argv[2]
    kraken_filtering_decisions =  sys.argv[3]
    genome_length_path = kraken_db + "/library/species_genome_size.txt"
    read_length = int(sys.argv[4])
    paired = sys.argv[5]
    if str(paired) == 'True':
        read_length = read_length*2

    ##step two- reading files to DFs
    bracken_df = pd.read_csv(bracken_report, sep="\t")
    bracken_df['taxonomy_id'] = bracken_df['taxonomy_id'].astype('str')
    kraken_df = pd.read_csv(kraken_filtering_decisions, sep="\t")
    kraken_df['species_taxid'] = kraken_df['species_taxid'].astype('str')
    length_df = pd.read_csv(genome_length_path, sep="\t")

    ##step 3- calculating stats
    tmp_merged_df = pd.merge(bracken_df,length_df[['species_level_taxa','max','mean','median']], left_on='taxonomy_id', right_on='species_level_taxa')
    per_million_scaling = (tmp_merged_df['new_est_reads'].sum() / 1000000) # calculate how many millions of reads there are
    tmp_merged_df['fraction_total_reads'] = tmp_merged_df['new_est_reads']/tmp_merged_df['new_est_reads'].sum()
    tmp_merged_df['tmp_scaling'] = tmp_merged_df['fraction_total_reads']*(tmp_merged_df['median'].sum()/tmp_merged_df['median']) # scale fraction_total_reads to reflect difference in genome length - smaller genome should be given greater weight
    tmp_merged_df['rel_taxon_abundance'] = tmp_merged_df['tmp_scaling']/tmp_merged_df['tmp_scaling'].sum() # make sure that the scaling adds up to 1
    tmp_merged_df['genetic_abundance'] = tmp_merged_df['fraction_total_reads']
    tmp_merged_df['depth'] = (tmp_merged_df['new_est_reads']*read_length)/tmp_merged_df['median'] #which is estimation of copies
    tmp_merged_df['reads_per_million_bases'] = (tmp_merged_df['new_est_reads'] / (tmp_merged_df['median'] / 1000000)).round(4) # equivalent to RPK but with megabases instead of kilobases
    tmp_merged_df['reads_per_million_reads'] = (tmp_merged_df['new_est_reads'] / per_million_scaling).round(4) # reads per million total reads
    tmp_merged_df['RPMPM'] =  tmp_merged_df['new_est_reads'] / ((tmp_merged_df['median'] / 1000000)* (per_million_scaling)) #reads per million base pairs per million reads
    tmp_merged_df['copies_per_million_reads'] = tmp_merged_df['depth'] / (per_million_scaling).round(4)
    tmp_merged_df = tmp_merged_df.merge(kraken_df, how='left', left_on='taxonomy_id', right_on='species_taxid')

    ## step 4 - output
    tmp_merged_df.rename(columns={'median': 'median_genome_length', 'max_cov':'breadth'}, inplace=True)
    processed_report = tmp_merged_df.drop(['tmp_scaling', 'species_level_taxa', 'max','mean','species_taxid','superkingdom','max_uniq_minimizers','kept'], axis=1)
    processed_report.to_csv(bracken_report+'.scaled', sep="\t", index=False)

if __name__ == "__main__":
    main()
