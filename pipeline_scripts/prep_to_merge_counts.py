import sys

report = sys.argv[1]
kraken_db = sys.argv[2]

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

def taxid_to_lineage(taxid, taxon_name):
  # look up the specific taxid,
  # build the lineage using the dictionaries

  # first deal with the special case of unclassiifed
  if taxid == '0':
    return 'unclassified'

  # not unclassified - proceed
  lineage = taxid_to_rank[taxid] + '_' + taxon_name
  child, parent = taxid, None

  while not parent == '1':
    # look up child, add to lineage
    parent = child_to_parent[child]
    rank = taxid_to_rank[parent]
    lineage = rank + '_' + parent + '|' + lineage
    child = parent # needed for recursion
  return lineage

with open(report, 'r') as infile:
  with open(report + '.to_merge', 'w') as outfile:
    for line in infile:
      line=line.rstrip('\n').split('\t')
      # use the function to figure out what we want to call this line
      taxid, name = line[4], line[5].strip()
      proper_name = taxid_to_lineage(taxid, name)
      num_reads = line[1]
      outfile.write(proper_name + '\t' + num_reads + '\n')
