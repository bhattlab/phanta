# TBD - Phanta
### A fast, accurate workflow to simultaneously profile the prokaryotic, eukaryotic, and viral community directly from short-read gut metagenomes

#  For citations
If Phanta is helpful to your work, please kindly consider citing our manuscript!
TODO: insert link to preprint.

# Table of contents
1. [Quick Start](#quick-start)
	* [Installation](#installation)
	* [Test Your Installation](#test-your-installation)
	* [Basic Usage](#basic-usage)
	* [Main Outputs](#main-outputs)
2. [Advanced](#advanced)
	* [Advanced Usage](#advanced-usage)
	* [Additional Outputs](#additional-outputs)
	* [Provided Postprocessing Scripts](#provided-postprocessing-scripts)

# Quick Start
## Installation

**Step One - Clone the repository**

Clone the repository to the desired location on your system using the following command:

	git clone <insert link here>

TODO: replace with appropriate link.

**Step Two - Install conda, if not already installed**

Check whether you have conda installed by typing:

	conda --help

If this command is not recognized by your system, please follow the instructions provided [here](https://developers.google.com/earth-engine/guides/python_install-conda/) to install conda.

**Step Three - Create and activate a new conda environment**

Navigate to the location where you cloned the repository using the `cd` command. Then, create a new conda environment via the following command:

	conda env create -n new_env --file env.yaml

Activate the environment by typing:

	conda activate new_env

TODO: replace new_env with whatever we decide to call the workflow and similarly rename env.yaml.

**Step Four - Download the database of genomes**

Download the Kraken2/Bracken-compatible database of genomes by navigating to the desired folder on your system and executing the following command:

TODO: insert the command. Ideally wget-able.

This command should install the following files:
1. hash.k2d: ~31GB
2. taxo.k2d: ~21MB
3. opts.k2d: ~4KB
4. inspect.out: ~18MB
5. taxonomy/nodes.dmp: ~11MB
6. taxonomy/names.dmp: ~16MB
7. database.kraken: ~24GB
8. database150mers.kmer_distrib: ~25MB
9. database150mers.kraken: ~866MB

*Note*: you can check the size of each file by executing `du -hs insert_file_name_here`.

TODO: If the size of any of the files above changes, update both this file and the notes about memory in config.yaml and config_test.yaml.

## Test Your Installation

To test that you are ready to run XXX on your data, first create a new subdirectory of your cloned repository called `test_phanta`. Then navigate to `test_phanta` using `cd` and download the four .fq.gz files required for testing via the following command:

TODO: insert command to download.

The total size of the download should be YYY.

TODO: replace XXX with the decided name of the pipeline and YYY with the total size of the files.

Then edit two files contained in the testing subdirectory of your cloned repository.
1. Edit `samp_file.txt` by replacing `<path_to_cloned_repo>` in the four locations indicated with the path to your cloned repository.
2. Edit `config_test.yaml` by replacing:
* `<path_to_cloned_repo>` in the three locations indicated with the path to your cloned repository.
* `<path_to_downloaded_database>` in the one location indicated with the path to the database of genomes you downloaded during the install.

TODO: edit both of the files indicated above before submission, to make them consistent with the instructions provided above.

Finally, execute the following command after replacing `<path_to_cloned_repo>`: in the two locations indicated:

snakemake -s <path_to_cloned_repo>/Snakefile \
--configfile <path_to_cloned_repo>/testing/config_test.yaml --jobs 99 --cores 1 --max-threads 16

*Note:* Please replace the number provided to max-threads with the maximum number of threads you have available. **If you are in the Bhatt Lab**, you don't need the `--cores` and `--max-threads` options; rather, you can replace them with `--profile scg`



## Basic Usage
## Main Outputs

# Advanced
## Advanced Usage
## Additional Outputs
## Provided Postprocessing Scripts

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
