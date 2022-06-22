import sys

report, kraken_db, failed_file, sample = \
sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

# make a few helpful dictionaries

with open(kraken_db + '/taxonomy/nodes.dmp', 'r') as infile:

  # make a child to parent dictionary
  # and a taxid to rank dictionary
  child_to_parent = {}
  taxid_to_rank = {}
  for line in infile:
    line=line.rstrip('\n').split('\t')
    child, parent, rank = line[0], line[2], line[4]
    child_to_parent[child] = parent
    taxid_to_rank[child] = rank

# also want a taxid_to_name dictionary
# use the inspect.out file

with open(kraken_db + '/inspect.out', 'r') as infile:
  taxid_to_name = {}
  for line in infile:
    line=line.rstrip('\n').split('\t')
    taxid, name = line[4], line[5].strip()
    taxid_to_name[taxid] = name

# also make a set of the samples that failed Bracken
with open(failed_file, 'r') as infile:
  failed_samples = set()
  for line in infile:
    failed_samples.add(line.rstrip('\n'))

def taxid_to_lineages(taxid):
  # look up the specific taxid,
  # build the lineages using the dictionaries

  # first deal with the special case of unclassiifed
  if taxid == '0':
    return 'unclassified'

  # not unclassified - proceed
  rank = taxid_to_rank[taxid]
  lineage_taxids = rank + '_' + taxid
  lineage_names = rank + '_' + taxid_to_name[taxid]
  child, parent = taxid, None

  while not parent == '1':
    # look up child, add to lineages
    parent = child_to_parent[child]
    parent_rank = taxid_to_rank[parent]
    # look up the name of the parent too
    parent_name = taxid_to_name[parent]
    lineage_taxids = parent_rank + '_' + parent + '|' + lineage_taxids
    lineage_names = parent_rank + '_' + parent_name + '|' + lineage_names
    child = parent # needed for recursion
  return lineage_taxids, lineage_names

with open(report, 'r') as infile:
  with open(report + '.to_merge', 'w') as outfile:
    if sample in failed_samples:
      pass
    else:
      for line in infile:
        line=line.rstrip('\n').split('\t')
        # use the function to figure out what we want to call this line
        taxid = line[4]
        lin_taxids, lin_names = taxid_to_lineages(taxid)
        num_reads = line[1]
        outfile.write('\t'.join([lin_names, lin_taxids, num_reads]) + '\n')
