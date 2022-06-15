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
    d = profile_with_host.groupby('domain').sum()
    p = profile_with_host.groupby('phylum').sum()
    c = profile_with_host.groupby('class').sum()
    o = profile_with_host.groupby('order').sum()
    f = profile_with_host.groupby('family').sum()
    g = profile_with_host.groupby('genus').sum()
    #creating out file
    taxon = pd.concat([d,p, c, o, f, g])
    if taxon.iloc[1].dtype=='float': #normalize to 1 if relative abundance was given
        taxon = pd.concat([d/d.sum() , p/p.sum(), c/c.sum() , o/o.sum(), f/f.sum(), g/g.sum()])
    taxon.index.name = "Taxon"
    taxon.to_csv(out)


if __name__ == "__main__":
    main()
