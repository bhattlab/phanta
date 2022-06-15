import pandas as pd
import sys
#usage: calculate_host_abundance.py <merged counts table>  <host prediction file>  <path to outfile>
#usage: calculate_host_abundance.py counts_table.txt host_prediction.tsv host_counts.txt
#input###

def main():
    #input###
    input_counts = sys.argv[1] #merged counts
    host_file = sys.argv[2] # microbial host per species level taxonomy
    out = sys.argv[3]
    #reading inputs
    profile = pd.read_csv(input_counts, sep="\t")
    host_prediction = pd.read_csv(host_file, sep="\t")
    #filteing-in only viral species
    profile_viral_species = profile[(profile.Taxon_Lineage_with_Names.str.contains("superkingdom_Viruses")) & (profile.Taxon_Lineage_with_Names.str.contains("species"))]
    #merging dataframes by species taxonomy id
    species_taxa = profile_viral_species.Taxon_Lineage_with_IDs.str.split("_").str[-1]
    profile_viral_species.insert(loc=2, column='species_taxonomy', value=species_taxa.astype(int))
    profile_with_host = pd.merge(profile_viral_species, host_prediction, how='left', right_on='species_taxa', left_on='species_taxonomy')
    #sum counts/abundance per level
    profile_with_host['Host genus'].fillna("d__Unknown;p__Unknown;c__Unknown;o__Unknown;f__Unknown;g__unknown", inplace=True)
    profile_with_host['domain'] = profile_with_host['Host genus'].str.split(";").str[0:1].str.join(";")
    profile_with_host['phylum'] = profile_with_host['Host genus'].str.split(";").str[0:2].str.join(";")
    profile_with_host['class'] = profile_with_host['Host genus'].str.split(";").str[0:3].str.join(";")
    profile_with_host['order'] = profile_with_host['Host genus'].str.split(";").str[0:4].str.join(";")
    profile_with_host['family'] = profile_with_host['Host genus'].str.split(";").str[0:5].str.join(";")
    profile_with_host['genus'] = profile_with_host['Host genus'].str.split(";").str[0:6].str.join(";")
    profile_with_host.drop(columns=['species_taxonomy', 'species_taxa'], inplace=True)
    #creating out file
    taxon = pd.concat([profile_with_host.groupby('domain').sum(), profile_with_host.groupby('phylum').sum(), profile_with_host.groupby('class').sum(), profile_with_host.groupby('order').sum(), profile_with_host.groupby('family').sum(), profile_with_host.groupby('genus').sum()])
    taxon.index.name = "Taxon"
    taxon.to_csv(out)


if __name__ == "__main__":
    main()
