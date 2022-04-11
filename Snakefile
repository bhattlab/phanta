##### STEP ZERO - Import required modules

from os.path import join
import sys
import snakemake

##### STEP ONE - Get information from config file.

def get_sample_reads(sample_file):
  sample_reads = {}
  paired_end = ''
  with open(sample_file) as sf:
    for line in sf.readlines():
      line = line.rstrip('\n').split('\t')
      if len(line) == 1 or line[0] == 'Sample' or line[0] == '#Sample' or line[0].startswith('#'):
        continue
      else: # not header
        sample = line[0]

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
        sample_reads[sample] = reads

    return (sample_reads, paired_end)

# call function, determine whether reads are paired or single ended
sample_reads, paired_end = get_sample_reads(config['sample_file'])
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
    expand(join(outdir, "classification/{samp}.krak.report.filtered.bracken"), samp=sample_names)

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
    python scripts/filter_kraken_reports.py {input.krak_report} {params.db} \
    {params.cov_thresh_bacterial} {params.cov_thresh_viral} {params.minimizer_thresh_bacterial} \
    {params.minimizer_thresh_viral}
  """

##### STEP FOUR - Run Bracken on filtered Kraken2 report.

rule bracken:
  input:
    krak_report = join(outdir, "classification/{samp}.krak.report.filtered")
  output:
    join(outdir, "classification/{samp}.krak.report.filtered.bracken")
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
