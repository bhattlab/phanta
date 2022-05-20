# Phage abundance pipeline (TODO: replace with more creative name)
## Kraken2/Bracken-based pipeline to determine abundance and properties of phages and other microbes in short-read metagenomes
### With user-adjustable filtering to minimize false positive results

# USAGE

Prior to running the pipeline, clone this repository.

Then create a new environment as follows:

	conda env create -n phage_abund_env --file phage_abund_env.yaml

Activate the environment:

	conda activate phage_abund_env

Then edit the config.yaml file to suit your needs.

There are six parameters that can be adjusted by the user to change the true/false positive ratio. These are: 1) confidence_threshold, 2) cov_thresh_viral, 3) minimizer_thresh_viral, 4) cov_thresh_bacterial, 5) minimizer_thresh_bacterial, 6) filter_thresh. Each parameter is described in more detail in the config file, and suggested defaults are provided there.   

After editing the config file, change directory such that you are "in" the cloned repository.

	cd /path/to/cloned/repo

Now you can run the pipeline using Snakemake! I like to do things in the order below. 

-Do a dry run to verify everything is working as expected.

	snakemake --dryrun -s /path/to/Snakefile --configfile /path/to/configfile --jobs 999 --reason --profile scg

-Run the pipeline! 

	snakemake -s /path/to/Snakefile --configfile /path/to/configfile --jobs 999 --reason --profile scg 

Note: if you are not in the Bhatt Lab, you will need to delete the --profile flag and argument, or edit the argument to the --profile flag.

# OUTPUT  

The main outputs are found within the classification subdirectory, specifically:
- counts.txt
	- Rows are taxa (across taxonomic levels) and columns are samples
	- Each cell reports the total number of reads in this sample that were assigned to this taxon after Kraken2/filtering/Bracken. 
- counts_norm_out_of_tot.txt
	- Similar to counts.txt, but each count has been normalized out of the total number of reads in the relevant sample
- counts_norm_out_of_bracken_classified.txt 
	- Similar to counts.txt, but each count has been normalized out of the total number of Bracken-classified reads in the relevant sample
- merged_community_abundance.txt
	- Species-level version of counts_norm_out_of_bracken_classified.txt, where each value has been corrected for genome length.

To filter any of the first three tables to a given taxonomic level, you may use the script reduce_merged_table_to_specific_rank.py within the post_pipeline_scripts subdirectory. The necessary arguments to the script are: 1) full path to the original table (e.g., < output_directory > /counts.txt), and 2) the taxonomic level of interest (e.g., species, genus, superkingdom...)

To change the merged_community_abundance.txt to a higher level than species (e.g., genus, superkingdom), you may use the script merged_community_table_summed_to_higher_rank.py within the post_pipeline_scripts subdirectory. The necessary arguments to the script are: 1) full path to the Kraken2 database (which you also specified in the config file), 2) full path to merged_community_abundance.txt, 3) full path of desired output file, 4) taxonomic level of interest.

Additional useful outputs within the classification subdirectory include the following per-sample outputs:
- The original and filtered Kraken2 reports for each sample (.krak.report and .krak.report.filtered)
- The Bracken reports for each sample
	- species-level only: .krak.report.filtered.bracken
	- all taxonomic levels: .krak.report_bracken_species.filtered
- A version of the species-level Bracken report where the original fraction_total_reads column has been corrected in various ways for genome length (.krak.report.filtered.bracken.scaled). See especially the new community_abundance column.

Please note that if a sample's filtered Kraken report does not contain any species with more than filter_thresh reads (parameter #6, above), then .krak.report.filtered.bracken and .krak.report.filtered.bracken.scaled will be empty and .krak.report_bracken_species.filtered will not report read counts for any species. Higher taxonomic levels will still be there, with counts equal to or less than the original Kraken2-assigned value.
