# Phanta
## Rapidly quantify taxa from all domains of life, directly from short-read human gut metagenomes
### The foundation of this workflow is a comprehensive, virus-inclusive database of genomes with integrated taxonomic information

#  For citations
If you used Phanta in your work, please cite:
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
		* [Collapse Viral Abundances by Predicted Host](#collapse-viral-abundances-by-predicted-host)
		* [Calculate Viral Lifestyle Statistics](#calculate-viral-lifestyle-statistics)

TODO: make sure that table of contents is fully updated and accurate before submission.

# Quick Start
## Installation

**Step One - Clone the repository**

Clone the repository to the desired location on your system using the following command:

	git clone <insert link here>

TODO: replace with appropriate link.

**Step Two - Install conda, if not already installed**

If you do not already have conda installed, please install using the instructions provided [here](https://developers.google.com/earth-engine/guides/python_install-conda/).

**Step Three - Create and activate a new conda environment**

Create a new conda environment via the following command, replacing `/full/path/to/cloned/repo` with the appropriate path to your cloned repository:

	conda env create -n phanta_env --file /full/path/to/cloned/repo/phanta_env.yaml

Activate the environment by executing:

	conda activate phanta_env

**Step Four - Download Phanta's default database**

Download Phanta's default database of genomes by navigating to the desired directory on your system and executing the following commands:

	wget https://www.dropbox.com/sh/3ktsdqlcph6x95r/AACGSj0sxYV6IeUQuGAFPtk8a/database_V1.tar.gz

	tar xvzf database_V1.tar.gz

This command should download the following files:

Kraken2 database
1. hash.k2d: ~31GB
2. taxo.k2d: ~21MB
3. opts.k2d: ~4KB
4. seqid2taxid.map: ~461MB

Bracken database (built for use with 150bp reads)
1. database150mers.kmer_distrib: ~25MB

*Note*: Phanta can run with additional read lengths, as described under [Advanced Usage](#advanced-usage).

Additional files required for pipeline to run:
1. inspect.out: ~18MB
2. taxonomy/nodes.dmp: ~11MB
3. taxonomy/names.dmp: ~16MB
4. library/species_genome_size.txt: ~6.3MB

For use with post-processing scripts:
1. host_prediction_to_genus.tsv: ~2.6MB
2. species_name_to_vir_score.txt: ~1.6MB

*Note*: as described in the preprint, an alternative version of the default database was also created, in which prophage sequences have been "masked" in prokaryotic genomes. Please see [Advanced Usage](#advanced-usage) for more details.

## Test Your Installation

To test that you are ready to run Phanta on your data, navigate to your cloned repository using `cd` and download the four `.fq.gz` files required for testing via the following command:

	wget https://www.dropbox.com/s/o65ibd288ozfb5w/test_dataset.tar.gz

	tar xvzf test_dataset.tar.gz

Then edit two files contained in the `testing` subdirectory of your cloned repository.
1. Edit `samp_file.txt` by replacing `/full/path/to/cloned/repo` in the four locations indicated with the full path to your cloned repository.
2. Edit `config_test.yaml` by replacing:
* `/full/path/to/cloned/repo` in the three locations indicated with the full path to your cloned repository.
* `/full/path/to/downloaded/database` in the one location indicated with the full path to the database of genomes you downloaded during the install.

Finally, execute the Snakemake command below, after replacing:
1. `/full/path/to/cloned/repo` with the path to your cloned repository
2.  The number provided to `max-threads` with the maximum number of threads you have available. Note that if this number is greater than 16, you can (but don't need to) also increase the argument to `class_threads` in `config_test.yaml`.

**Note** At least 32GB memory is required. Also, you may have to replace the `--cores` and `max-threads` arguments with a profile for SLURM job submission depending on your configuration; example of how this is done [here](https://github.com/bhattlab/slurm).

	snakemake -s /full/path/to/cloned/repo/Snakefile \
	--configfile /full/path/to/cloned/repo/testing/config_test.yaml \
	--jobs 99 --cores 1 --max-threads 16

When execution has completed, please check that your `test_dataset` directory has an empty file called `pipeline_completed.txt`. You should also have two new subdirectories in `test_dataset` - `classification` and `final_merged_outputs` - which should have identical contents to the corresponding subdirectories in the `testing` subdirectory of your cloned repository.

## Basic Usage

For basic usage, replace the four paths at the top of the  provided `config.yaml` file as appropriate.

You do not need to make any additional changes **except** if: 1) you did not conduct 150bp sequencing, or 2) if your read files are not gzipped. In those cases, you may also need to change the `read_length` or `gzipped` parameters, which are described under [Advanced Usage](#advanced-usage).

After you have finished editing your config file, execute a similar Snakemake command to the one you used to [Test Your Installation](#test-your-installation), example below:

	snakemake -s /full/path/to/cloned/repo/Snakefile \
	--configfile /full/path/to/cloned/repo/config.yaml \
	--jobs 99 --cores 1 --max-threads 16

## Main Outputs

The main outputs are merged tables that list the abundance of each taxon, in each sample. Rows are taxa and columns are samples.

* `final_merged_outputs/counts.txt`: provides the number of read (pairs) assigned to each taxon

* `final_merged_outputs/relative_read_abundance.txt`: same as `counts.txt` but normalized out of the total number of reads in each sample that were ultimately assigned to any taxon during abundance estimation.

* `final_merged_outputs/relative_taxonomic_abundance.txt`: similar to `relative_read_abundance.txt` but abundances are corrected for genome length. In addition, only species (and not higher taxonomic levels) are included in this report.

For examples of the above outputs, please see the `testing/final_merged_outputs` subdirectory.

*Note*: To filter `counts.txt` or `relative_read_abundance.txt` to a specific taxonomic level (e.g., species, genus), or to change `relative_taxonomic_abundance.txt` to a higher taxonomic level than species, please refer to [Filtering Merged Tables to a Specific Taxonomic Level](#filtering-merged-tables-to-a-specific-taxonomic-level) under [Provided Postprocessing Scripts](#provided-postprocessing-scripts).

# Advanced
## Advanced Usage

This section contains a description of the additional parameters in the config file that were not mentioned under [Basic Usage](#basic-usage) but can be altered if desired.

### Parameters under *Specifications for step one - classification of metagenomic reads*

* `confidence_threshold` (default `0.1`). This parameter can range from 0 to 1. Higher values yield more confident classifications but reduce sensitivity. Please see [this link from the Kraken2 documentation](https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#confidence-scoring) for more details.
* `gzipped` (default `True`). This parameter should be `True` if your read files are gzipped, otherwise `False`.
* `class_mem` (default `32`). This parameter specifies the memory in GB used for the classification step.
* `class_threads` (default `16`). This parameter specifies the number of threads used for the classification step. Recall that you cannot specify more than your maximum number of threads available in the `snakemake` command that executes the pipeline.

### Parameters under *Specifications for step two - filtering false positive species*

* `cov_thresh_viral` (default `0.1`). This parameter can range from 0 to 1 and specifies a genome coverage requirement for a viral species to be considered a "true positive" in a sample. For example, if this parameter is 0.1, that means that for a viral species to be considered a true positive in a sample, at least one genome of the species must be at least 10% covered by sample reads.
	* Each genome's coverage is estimated by dividing:
		* The number of unique minimizers in the genome that are covered by sample reads, by
		* The total number of unique minimizers in the genome.
	* *Terminology note* - minimizers are very similar to kmers; for a more detailed description of what they are, please see [the Kraken2 paper](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1891-0).
* `minimizer_thresh_viral` (default `0`). This parameter can take any value >= 0 and specifies an additional requirement for a viral species to be considered true positive in a sample. E.g., if this parameter is 10, that means at least one genome of the species must have 10+ of its unique minimizers covered by sample reads.
* `cov_thresh_bacterial` and `minimizer_thresh_bacterial` are the analogous parameters for filtering bacterial species.

### Parameters under *Specifications for step three - per-species abundance estimation*

* `read_length` (default `150`). This parameter specifies the read length. Please note: if you change this value, you must first execute the following command to create an appropriate Bracken database:

		bracken-build -d /full/path/to/downloaded/database -t <threads> -l <read_length>

* `filter_thresh` (default `10`). This parameter specifies one last false positive species filter - how many sample reads must have been classified to species X (in step one) for it to be considered truly present in the sample? This parameter is specific to the Bracken tool used for abundance estimation and is equivalent to the threshold parameter described in the [original Bracken documentation](https://github.com/jenniferlu717/Bracken). Note that this filter is uniform across all types of species (e.g., viral, bacterial).  

### Additional parameters

* `database`. Phanta is typically run with the default database linked above under Step Four of [Installation](#installation). However, as described in our manuscript, an alternative version of Phanta's default database was also created, in which prophage sequences have been "masked" in prokaryotic genomes. The download link for this database is: *coming soon!*

* `delete_intermediate` (default `True`). Specify `True` if you would like intermediate outputs to be deleted, otherwise `False`. Intermediate outputs are per-sample outputs generated during the execution of Steps 1 and 2. Examples of these intermediate files can be found within the `testing/classification/intermediate` subdirectory of the cloned repository.

## Additional Outputs

In addition to the merged tables provided in the `final_merged_outputs` subdirectory (see [Main Outputs](#main-outputs)), the pipeline provides per-sample outputs in the `classification` subdirectory. Specifically:

* The files ending with `.krak.report_bracken_species.filtered` correspond to the [Kraken-style report](https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#sample-report-output-format) outputted by [Bracken](https://github.com/jenniferlu717/Bracken) and specify the per-sample abundances that underlie the creation of the final merged tables `counts.txt` and `relative_read_abundance.txt`. Unlike in the merged tables, taxa that are not present in the sample are not included.

* The files ending with `.krak.report.filtered.bracken.scaled` essentially correspond to per-sample versions of `final_merged_outputs/relative_taxonomic_abundance.txt`. Specifically see the `rel_taxon_abundance` column. Unlike in the merged table, taxa that are not present in the sample are not included.
	* **Note**: additional normalizations beyond relative taxonomic abundance are also provided - e.g., `reads_per_million_bases`, `reads_per_million_reads`, `reads_per_million_bases_per_million_reads (RPMPM)`, `copies_per_million_reads`.

There are two final outputs worth noting:
1. `samples_that_failed_bracken.txt` in the `classification` subdirectory. This file contains names of samples that did not ultimately have any reads directly assigned to the species level during step three of the workflow. Please note that for these samples, the `.krak.report.filtered.bracken.scaled` file will be empty and there may be additional associated files in the `classification` subdirectory that end with `.temp`.
2. `total_reads.tsv` in the `final_merged_outputs` subdirectory. This file contains information about the total number of reads assigned to taxa in each sample, at various steps of the pipeline. Specifically:
- `Tot_Samp_Reads`: total number of reads in the original sample
- `Unassigned_Step_One`: number of reads that were not assigned a classification by Kraken2 during the classification step
- `Assigned_Step_Three`: sum total of reads assigned to a taxon after filtering false positive species and estimating species-level abundances
- `Unassigned_Step_Three`: difference between `Tot_Samp_Reads` and `Assigned_Step_Three`

Note that the normalization used to create `final_merged_outputs/relative_read_abundance.txt` from `final_merged_outputs/counts.txt` utilizes the `Assigned_Step_Three` column of `total_reads.tsv`.

## Provided Postprocessing Scripts

These scripts are provided within the `post_pipeline_scripts` subdirectory of the cloned repository.

### Filtering Merged Tables to a Specific Taxonomic Level

There are two scripts provided for this purpose.

**Script one**

`post_pipeline_scripts/reduce_merged_table_to_specific_rank.py` is a Python script that can be utilized to filter `final_merged_outputs/counts.txt` or `final_merged_outputs/relative_read_abundance.txt` to a given taxonomic level.

The necessary command-line arguments to the script are, in order:
1. Full path to the merged table, and
2. The taxonomic level of interest (e.g., species, genus, superkingdom...)

An example command is:

	python reduce_merged_table_to_specific_rank.py /full/path/to/counts.txt genus

The output of the above command would be a file called `counts_genus.txt` in the same directory as the original `counts.txt`.


**Script Two**

`post_pipeline_scripts/sum_corrected_relab_to_higher_level.py` is a Python script that can be used to sum up the species-level, genome length-corrected relative abundances provided in `final_merged_outputs/relative_taxonomic_abundance.txt` to a higher taxonomic level of interest (e.g., genus, superkingdom).

The necessary command-line arguments to the script are, in order:
1. Full path to the downloaded database of genomes
2. Full path to `final_merged_outputs/relative_taxonomic_abundance.txt`
3. Full path of desired output file, including the desired file name
4. Taxonomic level of interest

### Collapse Viral Abundances by Predicted Host
`post_pipeline_scripts/collapse_viral_abundances_by_host.py` is script that collapses viral abundances in each sample by predicted host.

Expected arguments are:
1. merged abundance file generated by Phanta (e.g., `final_merged_outputs/counts.txt`)
2. host assignment file (provided with the default database at `/full/path/to/downloaded/database/host_prediction_to_genus.tsv`). *Note:* the host assignment file has two columns: 1) taxonomy ID of viral species, 2) predicted lineage of host genus, in the following format: d_Bacteria;p_Proteobacteria;c_Gammaproteobacteria;o_Enterobacterales;f_Enterobacteriaceae;g_Escherichia
3. full desired path to output file (including file name)

As of preprint posting, the script collapses the viral abundances in the input merged abundance file by predicted host genus. So, the output file is a table where predicted host genera are rows, columns are samples, and each cell provides the abundance of viruses with a particular predicted host genus in a particular sample.

Usage:

	python  collapse_viral_abundances_by_host.py <merged abundance table>  <host assignment file>  <path to outfile>

### Calculate Viral Lifestyle Statistics

`post_pipeline_scripts/calculate_lifestyle_stats/lifestyle_stats.R` is an R script that can be used to calculate overall statistics about the lifestyles of the viruses present in each sample (e.g., abundance ratio of temperate to virulent phages). Calculations are based on per-species lifestyle predictions that were made using the tool BACPHLIP, for the default database described in the preprint. These per-species predictions are provided with the default database at `/database/species_name_to_vir_score.txt`.

The necessary command-line arguments to the R script are, in order:

1. The BACPHLIP-predicted virulence score above which a virus should be considered 'virulent' (suggestion: `0.5`).
2. The full path to the `species_name_to_vir_score.txt` file
3. The full path to a species-level version of `final_merged_outputs/counts.txt` (please see [Filtering Merged Tables to a Specific Taxonomic Level](#filtering-merged-tables-to-a-specific-taxonomic-level))
4. The full path to `final_merged_outputs/relative_taxonomic_abundance.txt` (or a species-level version of `final_merged_outputs/relative_read_abundance.txt`)
5. The desired name for the output file (full path)

An example output file, based on the testing dataset, is located in the same directory as the R script (`post_pipeline_scripts/calculate_lifestyle_stats/example_lifestyle_stats.txt`).

TODO: add correlation script (?)
