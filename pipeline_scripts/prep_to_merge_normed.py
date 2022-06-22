import sys

tot_reads_file, indir, failed = \
sys.argv[1], sys.argv[2], sys.argv[3]

# make a dictionary from sample name to number of Bracken-classified reads
with open(tot_reads_file, 'r') as infile:
  samp_name_to_reads = {}
  header=infile.readline() # skip
  for line in infile:
    line=line.rstrip('\n').split('\t')
    samp, brack_reads = line[0], line[3]
    samp_name_to_reads[samp] = brack_reads

sample_names = samp_name_to_reads.keys()

# make a set of failed samples
with open(failed, 'r') as infile:
  failed_samples = set()
  for line in infile:
    failed_samples.add(line.rstrip('\n'))

for samp in sample_names:
  # file to normalize
  counts_table = indir + '/' + samp + '.krak.report_bracken_species.filtered.to_merge'

  # file to produce
  outf = counts_table + '.norm_brack'

  with open(counts_table, 'r') as infile:
    with open(outf, 'w') as outfile:
      if samp in failed_samples:
        pass
      else:
        # look up bracken_classified_reads
        brack_classified_reads = int(samp_name_to_reads[samp])
        for line in infile:
          line=line.rstrip('\n').split('\t')
          lin_names, lin_taxids, num_reads = line[0], line[1], float(line[2])
          frac_reads_brack = str(round(num_reads/brack_classified_reads, 10))
          outfile.write('\t'.join([lin_names, lin_taxids, frac_reads_brack]) + '\n')
