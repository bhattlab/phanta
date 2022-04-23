import sys

tot_reads_file = sys.argv[1]

# make a dictionary from sample name to total number of reads and number of Bracken-classified reads
with open(tot_reads_file, 'r') as infile:
  samp_name_to_reads = {}
  header=infile.readline() # skip
  for line in infile:
    line=line.rstrip('\n').split('\t')
    samp, tot_reads, brack_reads = line[0], int(line[1]), int(line[3])
    samp_name_to_reads[samp] = [tot_reads, brack_reads]

sample_names = samp_name_to_reads.keys()

for samp in sample_names:
  # file to normalize
  counts_table = tot_reads_file[:tot_reads_file.rfind('/')] + \
  '/' + samp + '.krak.report_bracken_species.filtered.to_merge'

  # files to produce
  outf1 = counts_table + '.norm_tot'
  outf2 = counts_table + '.norm_brack'

  # look up total_reads, bracken_classified_reads
  total_reads = samp_name_to_reads[samp][0]
  brack_classified_reads = samp_name_to_reads[samp][1]

  with open(counts_table, 'r') as infile:
    with open(outf1, 'w') as outfile1:
      with open(outf2, 'w') as outfile2:
        for line in infile:
          line=line.rstrip('\n').split('\t')
          taxon_name, num_reads = line[0], float(line[1])
          frac_reads_tot = str(round(num_reads/total_reads, 4))
          frac_reads_brack = str(round(num_reads/brack_classified_reads, 4))
          outfile1.write(taxon_name + '\t' + frac_reads_tot + '\n')
          outfile2.write(taxon_name + '\t' + frac_reads_brack + '\n')
