# TBD - Phanta
### A fast, accurate workflow to simultaneously profile prokaryotes, eukaryotes, and viruses directly from short-read metagenomes originating from the human gut

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
		* [Filtering Merged Tables to a Specific Taxonomic Level](#filtering-merged-tables-to-a-specific-taxonomic-level)

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
1. Edit `samp_file.txt` by replacing `/full/path/to/cloned/repo` in the four locations indicated with the full path to your cloned repository.
2. Edit `config_test.yaml` by replacing:
* `/full/path/to/cloned/repo` in the three locations indicated with the full path to your cloned repository.
* `/full/path/to/downloaded/database` in the one location indicated with the full path to the database of genomes you downloaded during the install.

TODO: edit both of the files indicated above before submission, to make them consistent with the instructions provided above.

Finally, execute the following command after replacing `/full/path/to/cloned/repo`: in the two locations indicated:

	snakemake -s /full/path/to/cloned/repo/Snakefile \
	--configfile /full/path/to/cloned/repo/testing/config_test.yaml \
	--jobs 99 --cores 1 --max-threads 16

Since this command will take some time to finish, **it is recommended to run this command in a `tmux` session** or similar setup.

*Note:* Please replace the number provided to max-threads with the maximum number of threads you have available. Note that if this number is greater than 16, you can (but don't need to) also change the argument to `class_threads` in `config_test.yaml`. **If you are in the Bhatt Lab**, you don't need the `--cores` and `--max-threads` options; rather, you can replace them with `--profile scg`

When execution has completed, please check that your `test_phanta` has an empty file called `pipeline_completed.txt`. You should also have two new subdirectories in `test_phanta` - `classification` and `final_merged_outputs` - which should have identical contents to the corresponding subdirectories in the `testing` subdirectory of your cloned repository.

## Basic Usage

For basic usage, copy the provided `config.yaml` file and replace the four paths at the top of the the file as appropriate.

You do not need to make any additional changes **except** if: 1) you did not conduct 150bp sequencing, or 2) if your read files are not gzipped. In those cases, you may also need to change the `read_length` or `gzipped` parameters, which are described under [Advanced Usage](#advanced-usage).

After you have finished editing your config file, execute the same Snakemake command you used to [Test Your Installation](#test-your-installation), simply replacing the path to the `config_test` file with the path to the new edited config file.

## Main Outputs

The main outputs are merged tables that list the abundance of each taxon, in each sample.

* `final_merged_outputs/counts.txt`: gives the number of read (pairs) assigned to each taxon

* `final_merged_outputs/relative_abundance.txt`: same as `counts.txt` but normalized out of the total number of reads in each sample that were ultimately assigned to any taxon during abundance estimation.

* `final_merged_outputs/corrected_relative_abundance.txt`: same as `relative_abundance.txt` but corrected for genome length. Only species (and not higher taxonomic levels) are included in this report.

TODO: Edit the above as needed as we change the names of things, etc.

For examples of the above outputs, please see the `testing/final_merged_outputs` subdirectory.

*Note*: To filter `counts.txt` or `relative_abundance.txt` to a specific taxonomic level (e.g., species, genus), or to change `corrected_relative_abundance.txt` to a higher taxonomic level than species, please refer to [Filtering Merged Tables to a Specific Taxonomic Level](#filtering-merged-tables-to-a-specific-taxonomic-level) under [Provided Postprocessing Scripts](#provided-postprocessing-scripts).

# Advanced
## Advanced Usage

This section contains a description of the additional parameters in the config file that were not mentioned under [Basic Usage](#basic-usage) but can be altered if desired.

### Parameters under *Specifications for step one - classification of metagenomic reads*

* `confidence_threshold` (default `0.1`). This parameter can range from 0 to 1. Higher values yield more confident classifications but reduce sensitivity. Please see [this link from the Kraken2 documentation](#https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#confidence-scoring) for more details.
* `gzipped` (default `True`). This parameter should be `True` if your read files are gzipped, otherwise `False`.
* `class_mem` (default `32`). This parameter specifies the memory in GB used for the classification step. As of preprint publication, this value must be at least `32`.
* `class_threads` (default `16`). This parameter specifies the number of threads used for the classification step. If more threads are available, this parameter can be increased; otherwise, there is no need to change it. Recall that the maximum number of threads must be specified in the `snakemake` command that executes the pipeline.

### Parameters under *Specifications for step two - filtering false positive species*

* `cov_thresh_viral` (default `0.1`). This parameter can range from 0 to 1 and essentially specifies a genome coverage requirement for a viral species be considered a "true positive" in a sample. For example, if this parameter is 0.1, that means that for a viral species to be considered a true positive in a sample, at least one genome in the species must be at least 10% covered by sample reads.
	* Genome coverage is estimated by dividing the number of unique minimizers in the genome that are covered by sample reads, by the total number of unique minimizers in the genome.
	* Minimizers are very similar to kmers; for a more detailed description of what they are, please see [the Kraken2 paper](#https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1891-0)
* `minimizer_thresh_viral` (default `0`). This parameter can take any value >= 0 and specifies an additional requirement, beyond genome coverage, for a viral species to be considered a "true positive" in a sample. For example, if this parameter is 10, that means that for a viral species to be considered a true positive in a sample, at least one genome in the species must have 10+ of its unique minimizers covered by sample reads.
* `cov_thresh_bacterial` and `minimizer_thresh_bacterial` are the analogous parameters for filtering bacterial species.

### Parameters under *Specifications for step three - per-species abundance estimation*

## Additional Outputs
## Provided Postprocessing Scripts

### Filtering Merged Tables to a Specific Taxonomic Level

# OLD - OUTPUT  

To filter any of the first three tables to a given taxonomic level, you may use the script reduce_merged_table_to_specific_rank.py within the post_pipeline_scripts subdirectory. The necessary arguments to the script are: 1) full path to the original table (e.g., < output_directory > /counts.txt), and 2) the taxonomic level of interest (e.g., species, genus, superkingdom...)

To change the merged_community_abundance.txt to a higher level than species (e.g., genus, superkingdom), you may use the script merged_community_table_summed_to_higher_rank.py within the post_pipeline_scripts subdirectory. The necessary arguments to the script are: 1) full path to the Kraken2 database (which you also specified in the config file), 2) full path to merged_community_abundance.txt, 3) full path of desired output file, 4) taxonomic level of interest.

Additional useful outputs within the classification subdirectory include the following per-sample outputs:
- The original and filtered Kraken2 reports for each sample (.krak.report and .krak.report.filtered)
- The Bracken reports for each sample
	- species-level only: .krak.report.filtered.bracken
	- all taxonomic levels: .krak.report_bracken_species.filtered
- A version of the species-level Bracken report where the original fraction_total_reads column has been corrected in various ways for genome length (.krak.report.filtered.bracken.scaled). See especially the new community_abundance column.

Please note that if a sample's filtered Kraken report does not contain any species with more than filter_thresh reads (parameter #6, above), then .krak.report.filtered.bracken and .krak.report.filtered.bracken.scaled will be empty and .krak.report_bracken_species.filtered will not report read counts for any species. Higher taxonomic levels will still be there, with counts equal to or less than the original Kraken2-assigned value.
