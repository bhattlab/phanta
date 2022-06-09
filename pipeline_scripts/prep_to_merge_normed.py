import sys

tot_reads_file = sys.argv[1]
indir = sys.argv[2]

# make a dictionary from sample name to number of Bracken-classified reads
with open(tot_reads_file, 'r') as infile:
  samp_name_to_reads = {}
  header=infile.readline() # skip
  for line in infile:
    line=line.rstrip('\n').split('\t')
    samp, brack_reads = line[0], int(line[3])
    samp_name_to_reads[samp] = brack_reads

sample_names = samp_name_to_reads.keys()

for samp in sample_names:
  # file to normalize
  counts_table = indir + '/' + samp + '.krak.report_bracken_species.filtered.to_merge'

  # file to produce
  outf = counts_table + '.norm_brack'

  # look up bracken_classified_reads
  brack_classified_reads = samp_name_to_reads[samp]

  with open(counts_table, 'r') as infile:
    with open(outf, 'w') as outfile:
      for line in infile:
        line=line.rstrip('\n').split('\t')
        taxon_name, num_reads = line[0], float(line[1])
        frac_reads_brack = str(round(num_reads/brack_classified_reads, 10))
        outfile.write(taxon_name + '\t' + frac_reads_brack + '\n')
