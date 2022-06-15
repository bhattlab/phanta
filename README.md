# Phanta
## Rapidly quantify taxa from all domains of life, directly from short-read gut metagenomes
### The foundation of this workflow is a comprehensive, virome-aware database of genomes with integrated taxonomic information

#  For citations
If Phanta is helpful to your work, please consider citing our manuscript!
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
		* [Virulence Score Calculator](#virulence-score-calculator)

# Quick Start
## Installation

**Step One - Clone the repository**

Clone the repository to the desired location on your system using the following command:

	git clone <insert link here>

TODO: replace with appropriate link.

**Step Two - Install conda, if not already installed**

Check whether you have conda installed by executing:

	conda --help

If this command is not recognized by your system, please follow the instructions provided [here](https://developers.google.com/earth-engine/guides/python_install-conda/) to install conda.

**Step Three - Create and activate a new conda environment**

Navigate to the location where you cloned the repository using the `cd` command. Then, create a new conda environment via the following command:

	conda env create -n new_env --file env.yaml

Activate the environment by executing:

	conda activate new_env

TODO: replace new_env with whatever we decide to call the workflow and similarly rename env.yaml.

**Step Four - Download the database of genomes**

Download the Kraken2/Bracken-compatible database of genomes by navigating to the desired directory on your system and executing the following command:

TODO: insert the command. Ideally wget-able.

This command should download the following files:
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

To test that you are ready to run XXX on your data, first create a new subdirectory of your cloned repository called `test_phanta`. Then navigate to `test_phanta` using `cd` and download the four `.fq.gz` files required for testing via the following command:

TODO: insert command to download.

The total size of the download should be YYY.

TODO: replace XXX with the decided name of the pipeline and YYY with the total size of the files.

Then edit two files contained in the testing subdirectory of your cloned repository.
1. Edit `samp_file.txt` by replacing `/full/path/to/cloned/repo` in the four locations indicated with the full path to your cloned repository.
2. Edit `config_test.yaml` by replacing:
* `/full/path/to/cloned/repo` in the three locations indicated with the full path to your cloned repository.
* `/full/path/to/downloaded/database` in the one location indicated with the full path to the database of genomes you downloaded during the install.

TODO: edit both of the files indicated above before submission, to make them consistent with the instructions provided above.

Finally, execute the Snakemake command below, after replacing:
1. `/full/path/to/cloned/repo` with the path to your cloned repository
2.  The number provided to `max-threads` with the maximum number of threads you have available. Note that if this number is greater than 16, you can (but don't need to) also increase the argument to `class_threads` in `config_test.yaml`.

**If you are in the Bhatt Lab**, you don't need the `--cores` and `--max-threads` options; rather, you can replace them with `--profile scg`

Since the command will take some time to finish, **it is recommended to execute it in a `tmux` session** or similar setup.

	snakemake -s /full/path/to/cloned/repo/Snakefile \
	--configfile /full/path/to/cloned/repo/testing/config_test.yaml \
	--jobs 99 --cores 1 --max-threads 16

When execution has completed, please check that your `test_phanta` directory has an empty file called `pipeline_completed.txt`. You should also have two new subdirectories in `test_phanta` - `classification` and `final_merged_outputs` - which should have identical contents to the corresponding subdirectories in the `testing` subdirectory of your cloned repository.

## Basic Usage

For basic usage, copy the provided `config.yaml` file and replace the four paths at the top of the the file as appropriate.

You do not need to make any additional changes **except** if: 1) you did not conduct 150bp sequencing, or 2) if your read files are not gzipped. In those cases, you may also need to change the `read_length` or `gzipped` parameters, which are described under [Advanced Usage](#advanced-usage).

After you have finished editing your config file, execute the same Snakemake command you used to [Test Your Installation](#test-your-installation), simply replacing the path to the `config_test` file with the path to the new edited config file.

## Main Outputs

The main outputs are merged tables that list the abundance of each taxon, in each sample. Rows are taxa and columns are samples.

* `final_merged_outputs/counts.txt`: gives the number of read (pairs) assigned to each taxon

* `final_merged_outputs/relative_abundance.txt`: same as `counts.txt` but normalized out of the total number of reads in each sample that were ultimately assigned to any taxon during abundance estimation.

* `final_merged_outputs/corrected_relative_abundance.txt`: same as `relative_abundance.txt` but abundances are corrected for genome length. Only species (and not higher taxonomic levels) are included in this report.

TODO: Edit the above as needed as we change the names of things, etc.

For examples of the above outputs, please see the `testing/final_merged_outputs` subdirectory.

*Note*: To filter `counts.txt` or `relative_abundance.txt` to a specific taxonomic level (e.g., species, genus), or to change `corrected_relative_abundance.txt` to a higher taxonomic level than species, please refer to [Filtering Merged Tables to a Specific Taxonomic Level](#filtering-merged-tables-to-a-specific-taxonomic-level) under [Provided Postprocessing Scripts](#provided-postprocessing-scripts).

# Advanced
## Advanced Usage

This section contains a description of the additional parameters in the config file that were not mentioned under [Basic Usage](#basic-usage) but can be altered if desired.

### Parameters under *Specifications for step one - classification of metagenomic reads*

* `confidence_threshold` (default `0.1`). This parameter can range from 0 to 1. Higher values yield more confident classifications but reduce sensitivity. Please see [this link from the Kraken2 documentation](https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#confidence-scoring) for more details.
* `gzipped` (default `True`). This parameter should be `True` if your read files are gzipped, otherwise `False`.
* `class_mem` (default `32`). This parameter specifies the memory in GB used for the classification step. As of preprint publication, this value must be at least `32`.
* `class_threads` (default `16`). This parameter specifies the number of threads used for the classification step. If more threads are available, this parameter can be increased; otherwise, there is no need to change it. Recall that you must specify the maximum number of threads available in the `snakemake` command that executes the pipeline.

### Parameters under *Specifications for step two - filtering false positive species*

* `cov_thresh_viral` (default `0.1`). This parameter can range from 0 to 1 and essentially specifies a genome coverage requirement for a viral species be considered a "true positive" in a sample. For example, if this parameter is 0.1, that means that for a viral species to be considered a true positive in a sample, at least one genome in the species must be at least 10% covered by sample reads.
	* Each genome's coverage is estimated by dividing:
		* The number of unique minimizers in the genome that are covered by sample reads, by
		* The total number of unique minimizers in the genome.
	* *Terminology note* - minimizers are very similar to kmers; for a more detailed description of what they are, please see [the Kraken2 paper](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1891-0).
* `minimizer_thresh_viral` (default `0`). This parameter can take any value >= 0 and specifies an additional requirement, beyond genome coverage, for a viral species to be considered a "true positive" in a sample. For example, if this parameter is 10, that means that for a viral species to be considered a true positive in a sample, at least one genome in the species must have 10+ of its unique minimizers covered by sample reads.
* `cov_thresh_bacterial` and `minimizer_thresh_bacterial` are the analogous parameters for filtering bacterial species.

### Parameters under *Specifications for step three - per-species abundance estimation*

* `read_length` (default `150`). This parameter specifies the read length. Please note: if you change this, you must first execute the following command, replacing the `/full/path/to/downloaded/database` with the appropriate path, and the `read_len` with the appropriate read length (e.g., 100). If you have fewer than 10 threads available, you will also need to change the argument to `-t`.

		bracken-build -d /full/path/to/downloaded/database -t 10 -l read_len

* `filter_thresh` (default `10`). This parameter specifies one last false positive species filter - how many sample reads must have been classified to species X in step one for it to be considered truly present in the sample? This parameter is specific to the Bracken tool that is utilized in abundance estimation and is equivalent to the threshold parameter described in the [original Bracken documentation](https://github.com/jenniferlu717/Bracken). Note that this filter is uniform across all types of species (e.g., viral, bacterial).  

* `abund_est_mem` (default `26`). This parameter specifies the memory in GB used for the abundance estimation step. As of preprint publication, this value must be at least `26`.

### Additional parameters

* `delete_intermediate` (default `True`). Specify `True` if you would like intermediate outputs to be deleted, otherwise `False`. Intermediate outputs are per-sample outputs generated during the execution of Steps 1 and 2. Examples of these intermediate files can be found within the `testing/classification/intermediate` subdirectory of the cloned repository.

## Additional Outputs

In addition to the merged tables provided in the `final_merged_outputs` subdirectory (see [Main Outputs](#main-outputs)), the pipeline provides per-sample outputs in the `classification` subdirectory. Specifically:

* The files ending with `.krak.report_bracken_species.filtered` correspond to the [Kraken-style report](https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#sample-report-output-format) outputted by [Bracken](https://github.com/jenniferlu717/Bracken) and specify the per-sample abundances that underlie the creation of the final merged tables `counts.txt` and `relative_abundance.txt`. Unlike in the merged tables, taxa that are not present in the sample are not included.

* The files ending with `.krak.report.filtered.bracken.scaled` essentially correspond to per-sample versions of `final_merged_outputs/corrected_relative_abundance.txt`. Specifically see the `community_abundance` column. Unlike in the merged table, taxa that are not present in the sample are not included.
	* **Note**: additional normalizations beyond length-corrected relative abundance are also provided - e.g., `reads_per_million_bases`, `reads_per_million_reads`, `reads_per_million_bases_per_million_reads (RPMPM)`, `copies_per_million_reads`.

TODO: replace community abundance with whatever we decide to call it.

There are two final outputs worth noting:
1. `samples_that_failed_bracken.txt` in the `classification` subdirectory. This file contains names of samples that did not ultimately have any reads directly assigned to the species level. Please note that for these samples, the `.krak.report.filtered.bracken.scaled` file will be empty.
2. `total_reads.tsv` in the `final_merged_outputs` subdirectory. This file contains information about the total number of classified/unclassified reads in each sample, at various steps of the pipeline. Note that the normalization used to create `final_merged_outputs/relative_abundance.txt` from `final_merged_outputs/counts.txt` utilizes the `Classified_Step_Three` column of this file.

## Provided Postprocessing Scripts

These scripts are provided within the `post_pipeline_scripts` subdirectory of the cloned repository.

### Filtering Merged Tables to a Specific Taxonomic Level

There are two scripts provided for this purpose.
**Script One**
`post_pipeline_scripts/caclulate_host_abundance.py` is script that calculates host abundance;
Expected arguments are:
1. merged output file (e.g final_merged_outputs/counts.txt)
2. host assignment file (provided with the default database /database/host_prediction_to_genus.tsv . The format is species level taxonomy per virus, and predicted lineage of the host genus in the following format: d_Bacteria;p_Proteobacteria;c_Gammaproteobacteria;o_Enterobacterales;f_Enterobacteriaceae;g_Escherichia
3. path to outfile. It will return an OTU table for the host, based on the viral abundance and profiles the host landscape in all samples.
Usage:
python  calculate_host_abundance.py <merged counts table>  <host prediction file>  <path to outfile>

**Script Two**

`post_pipeline_scripts/reduce_merged_table_to_specific_rank.py` is a Python script that can be utilized to filter `final_merged_outputs/counts.txt` or `final_merged_outputs/relative_abundance.txt` to a given taxonomic level.

The necessary command-line arguments to the script are, in order:
1. Full path to the merged table, and
2. The taxonomic level of interest (e.g., species, genus, superkingdom...)

An example command is:

	python reduce_merged_table_to_specific_rank.py /full/path/to/counts.txt genus

The output of the above command would be a file called `counts_genus.txt` in the same directory as the original `counts.txt`.


**Script Three**

`post_pipeline_scripts/sum_corrected_relab_to_higher_level.py` is a Python script that can be used to sum up the species-level, genome length-corrected relative abundances provided in `final_merged_outputs/corrected_relative_abundance.txt` to a higher taxonomic level of interest (e.g., genus, superkingdom).

The necessary command-line arguments to the script are, in order:
1. Full path to the downloaded database of genomes
2. Full path to `final_merged_outputs/corrected_relative_abundance.txt`
3. Full path of desired output file, including the desired file name
4. Taxonomic level of interest

### Virulence Score Calculator

`post_pipeline_scripts/virulence_score_calculation/virulence_score_calculator.R` is an R script that can be used to estimate the overall virulence of the viral community in a sample, based on per-species virulence predictions that were made using the tool BACPHLIP, for the database described in the preprint. These per-species predictions are listed in the file `post_pipeline_scripts/virulence_score_calculation/species_name_to_vir_score.txt`.

The necessary command-line arguments to the R script are, in order:
1. The full path to the `species_name_to_vir_score.txt` file
2. The full path to `final_merged_outputs/corrected_relative_abundance.txt`
3. The desired output directory for the output of the script

The output of the script is a two-column table called `virulence_scores_per_sample.txt`. An example output, based on the testing dataset, is located in the same directory as the R script (`post_pipeline_scripts/virulence_score_calculation/`).

TODO: link to preprint above.

TODO: Add the additional scripts uploaded by Yishay.
