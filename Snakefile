##### STEP ZERO - Import required modules

from os.path import join
import sys
import snakemake

##### STEP ONE - Get information from config file.

def get_sample_reads(sample_file):
  sample_reads = {}
  paired_end = ''
  with open(sample_file, 'r') as sf:
    for line in sf:
      print(line)
      line = line.rstrip('\n').split('\t')
      if len(line) == 1 or line[0] == 'Sample' or line[0] == '#Sample' or line[0].startswith('#'):
        continue
      else: # not header
        sample = line[0]
        #print(sample)
      if (len(line) == 3): # paired end
        reads = [line[1], line[2]]
        if paired_end != '' and not paired_end:
          sys.exit('All samples must be paired or single ended.')
        paired_end = True

      elif (len(line) == 2): # single end specified
        reads = [line[1]]
        if paired_end != '' and paired_end:
          sys.exit('All samples must be paired or single ended.')
        paired_end = False

      if sample in sample_reads:
        raise ValueError("Non-unique sample encountered!")
      else:
        #print('here')
        sample_reads[sample] = reads

    return (sample_reads, paired_end)

# call function, determine whether reads are paired or single ended
sample_reads, paired_end = get_sample_reads(config['sample_file'])

#print(sample_reads, paired_end)

if paired_end:
  paired_string = '--paired'
else:
  paired_string = ''
sample_names = sample_reads.keys()

# also determine whether gzipped
# print(config['gzipped'] == True)
if config['gzipped'] == True:
   gzipped_string = '--gzip-compressed'
else:
   gzipped_string = ''

# also read in desired confidence threshold for Kraken
confidence_threshold = config['confidence_threshold']

# define output directory
outdir = config['outdir']

##### STEP TWO - Define desired pipeline outputs.

rule all:
  input:
    expand(join(outdir, "classification/{samp}.krak.report.filtered.bracken.tsv"), samp=sample_names),
    expand(join(outdir, "classification/{samp}.krak.report_bracken_species.filtered.to_merge"), samp=sample_names),
    join(outdir, "classification/total_reads.tsv")

##### STEP THREE - Run Kraken2, and filter report based on user-defined thresholds.

rule kraken:
  input:
    reads = lambda wildcards: sample_reads[wildcards.samp]
  output:
    krak = join(outdir, "classification/{samp}.krak"),
    krak_report = join(outdir, "classification/{samp}.krak.report")
  params:
    db = config['database'],
    paired_string = paired_string,
    gzipped_string = gzipped_string,
    confidence_threshold = confidence_threshold
  threads: 8
  resources:
    mem=256,
    time=6
  shell: """
    kraken2 --db {params.db} --threads {threads} --output {output.krak} \
    --report {output.krak_report} --report-minimizer-data {params.paired_string} \
    {params.gzipped_string} {input.reads} --confidence {params.confidence_threshold}
    """

rule filter_kraken:
  input:
    krak_report = join(outdir, "classification/{samp}.krak.report")
  output:
    krak_species = temp(join(outdir, "classification/{samp}.krak.report.species")),
    krak_species_final = join(outdir, "classification/{samp}.krak.report.species.final"),
    krak_report_filtered = join(outdir, "classification/{samp}.krak.report.filtered"),
    filtering_decisions = join(outdir, "classification/{samp}.krak.report.filtering_decisions.txt")
  params:
    db = config['database'],
    cov_thresh_bacterial = config['cov_thresh_bacterial'],
    cov_thresh_viral = config['cov_thresh_viral'],
    minimizer_thresh_bacterial = config['minimizer_thresh_bacterial'],
    minimizer_thresh_viral = config['minimizer_thresh_viral']
  shell: """
    python pipeline_scripts/filter_kraken_reports.py {input.krak_report} {params.db} \
    {params.cov_thresh_bacterial} {params.cov_thresh_viral} {params.minimizer_thresh_bacterial} \
    {params.minimizer_thresh_viral}
  """

##### STEP FOUR - Run Bracken on filtered Kraken2 report.

rule bracken:
  input:
    krak_report = join(outdir, "classification/{samp}.krak.report.filtered")
  output:
    brack_report_1 = join(outdir, "classification/{samp}.krak.report.filtered.bracken"),
    brack_report_2 = join(outdir, "classification/{samp}.krak.report_bracken_species.filtered")
  params:
    db = config['database'],
    readlen = config['read_length'],
    level = config['taxonomic_level'],
    threshold = config['filter_thresh'],
    outspec = join(outdir, "classification/{samp}.krak.report.filtered.bracken"),
  threads: 1
  resources:
    mem = 64,
    time = 1
  shell: """
    bracken -d {params.db} -i {input.krak_report} -o {params.outspec} -r {params.readlen} \
    -l {params.level} -t {params.threshold}
    """
##### STEP FIVE - Merge final Bracken reports into usable tables - 1) counts table, 2) normalized counts - normalize by TOTAL READS in sample, 3) normalized counts - normalize by BRACKEN-CLASSIFIED READS in sample.

rule prepare_to_merge: # do this rule for each Bracken report individually
  input:
    brack_report = join(outdir, "classification/{samp}.krak.report_bracken_species.filtered")
  output:
    brack_to_merge = join(outdir, "classification/{samp}.krak.report_bracken_species.filtered.to_merge")
  params:
    db = config['database']
  shell: """
    python pipeline_scripts/prepare_brack_report_for_merging.py {input.brack_report} {params.db}
    """

# Now we will calculate the total reads in each sample, for normalization
# Also calculate the total reads ultimately classified by Bracken

rule tot_reads_per_sample: # will need for normalization
  input:
    brack_report = join(outdir, "classification/{samp}.krak.report_bracken_species.filtered")
  output:
    tot_reads_file = temp(join(outdir, "classification/{samp}_total_reads.txt"))
  params:
    krak_brack_dir = join(outdir, "classification")
  shell: """
    bash pipeline_scripts/calc_total_reads.sh {wildcards.samp} \
    {params.krak_brack_dir} {output.tot_reads_file}
    """

rule tot_reads_all: # aggregate outputs of the previous rule
  input:
    expand(join(outdir, "classification/{samp}_total_reads.txt"), samp=sample_names)
  output:
    outf=join(outdir, "classification/total_reads.tsv")
  params:
    classdir=join(outdir, "classification")
  shell: """
    echo -e 'Samp_Name\tTot_Reads\tUnclassified_Krak\tBrack_Classified\tUnclassified_Brack' > {output.outf}
    cat {params.classdir}/*total_reads.txt >> {output.outf}
    """

##### STEP XXX - Correct species abundances reported by Bracken for genome length.

rule scale_bracken:
  input:
    bracken_report = join(outdir, "classification/{samp}.krak.report.filtered.bracken"),
    filtering_decisions = join(outdir, "classification/{samp}.krak.report.filtering_decisions.txt")
  output:
    join(outdir, "classification/{samp}.krak.report.filtered.bracken.tsv")
  params:
    db = config['database'],
    readlen = config['read_length'],
    paired = paired_end
  threads: 1
  shell: """
    python pipeline_scripts/scale_bracken.py {params.db} {input.bracken_report} \
    {input.filtering_decisions} {params.readlen} {params.paired}
    """
