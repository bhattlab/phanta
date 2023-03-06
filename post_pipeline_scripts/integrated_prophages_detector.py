import sys

# define command-line arguments
sample_file = sys.argv[1]
db = sys.argv[2]
scaled_bracken_reports = sys.argv[3]
se_fwd = sys.argv[4]
se_rev = sys.argv[5]
outfolder = sys.argv[6]

# define dictionaries and a function that will be helpful later

with open(db + '/taxonomy/nodes.dmp', 'r') as infile:
	# make a child to parent dictionary
	# and a taxid to rank dictionary
	child_to_parent = {}
	taxid_to_rank = {}
	for line in infile:
		line=line.rstrip('\n').split('\t')
		child, parent, rank = line[0], line[2], line[4]
		child_to_parent[child] = parent
		taxid_to_rank[child] = rank

def taxid_to_desired_rank(taxid, desired_rank):
	if taxid == '0':
		return 'unclassified'
	# look up the specific taxid,
	# build the lineage using the dictionaries
	# stop at the desired rank and return the taxid
	lineage = [[taxid, taxid_to_rank[taxid]]]
	if taxid_to_rank[taxid] == desired_rank:
		return taxid
	child, parent = taxid, None
	while not parent == '1':
		# print(child, parent)
		# look up child, add to lineage
		parent = child_to_parent[child]
		rank = taxid_to_rank[parent]
		lineage.append([parent, rank])
		if rank == desired_rank:
			return parent
		child = parent # needed for recursion
	return 'error - taxid above desired rank or has no annotation at this level'

# dictionary of sample to identified viruses
sample_to_viruses = {}
# dictionary of sample to identified bacteria
sample_to_bacteria = {}

# determine set of samples
with open(sample_file, 'r') as infile:
	samples = set()
	for line in infile:
		if not line.startswith('#'):
			sample = line.split('\t')[0]
			samples.add(sample)

# go through the samples, iterate through the relevant Bracken report
for sample in samples:
	viruses, bacteria = set(), set()
	b_report = scaled_bracken_reports + '/' + sample + '.krak.report.filtered.bracken.scaled'
	with open(b_report, 'r') as infile:
		header = infile.readline().rstrip('\n').split('\t')
		taxid_col = header.index('taxonomy_id')
		for line in infile:
			taxid = line.rstrip('\n').split('\t')[taxid_col]
			superkingdom = taxid_to_desired_rank(taxid, 'superkingdom')
			if superkingdom == '10239':
				viruses.add(taxid)
			elif superkingdom == '2':
				bacteria.add(taxid)
	sample_to_viruses[sample] = viruses
	sample_to_bacteria[sample] = bacteria

# iterate through krak files, find chimeric bacterial-virus read pairs
# only care if the bacteria and virus were both identified in the sample

# open the outfile
outf = outfolder + '/integrated_prophages_detection_results.txt'
with open(outf, 'w') as outfile:
	header = ['sample', 'identified_virus', 'mgv_prophage_evidence', 'identified_bacteria', 'correct_host_genus_mgv',
	'correct_host_species_mgv', 'chimeric_pairs']
	outfile.write('\t'.join(header) + '\n')

	for sample in samples:
		# dictionary - identified virus = key
		# value is a dictionary of identified bac to number of chimeric read pairs for this virus-bac pair]
		virus_to_bac_and_chimeric_reads = {}

		# get identified viruses and bacteria
		viruses_id, bacteria_id = sample_to_viruses[sample], \
		sample_to_bacteria[sample]

		with open(se_fwd + '/' + sample + '.krak', 'r') as fwd_run, \
		open(se_rev + '/' + sample + '.krak', 'r') as rev_run:

			for fwd_end, rev_end in zip(fwd_run, rev_run):

				viral_contender, bacterial_contender = False, False

				fwd_class = fwd_end.split('\t')[2]
				rev_class = rev_end.split('\t')[2]

				# get species and superkingdom level classifications
				fwd_species = taxid_to_desired_rank(fwd_class, 'species')
				fwd_kingdom = taxid_to_desired_rank(fwd_class, 'superkingdom')
				rev_species = taxid_to_desired_rank(rev_class, 'species')
				rev_kingdom = taxid_to_desired_rank(rev_class, 'superkingdom')

				kingdoms = {fwd_kingdom, rev_kingdom}
				if len(kingdoms) > 1:
					# scenario 1 - viral forward read, bacterial reverse read
					if (fwd_kingdom == '10239') and ('error' not in fwd_species) \
					and (rev_kingdom == '2') and ('error' not in rev_species):
						# record this info
						viral_contender = fwd_species
						bacterial_contender = rev_species

					# scenario 2 - viral reverse read, bacterial forward read
					if (rev_kingdom == '10239') and ('error' not in rev_species) \
					and (fwd_kingdom == '2') and ('error' not in fwd_species):
						# record this info
						viral_contender = rev_species
						bacterial_contender = fwd_species

					if viral_contender and bacterial_contender:
						# figure out whether we care about this virus-bac pair,
						# then if so, record in dict
						if viral_contender in viruses_id and bacterial_contender in bacteria_id:
							if viral_contender in virus_to_bac_and_chimeric_reads:
								entry = virus_to_bac_and_chimeric_reads[viral_contender]
								if bacterial_contender in entry:
									entry[bacterial_contender] += 1
								else:
									entry[bacterial_contender] = 1
							else:
								virus_to_bac_and_chimeric_reads[viral_contender] = {bacterial_contender:1}

		# now can output all the relevant information for this sample
		for virus in virus_to_bac_and_chimeric_reads:
			entry = virus_to_bac_and_chimeric_reads[virus]
			for bac in entry:
				number_reads = entry[bac]
				outline = [sample, virus, bac, str(number_reads)]
				outfile.write('\t'.join(outline) + '\n')
