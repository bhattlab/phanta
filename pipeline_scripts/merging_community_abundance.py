import sys

db, temp_file, outdir = sys.argv[1], sys.argv[2], sys.argv[3]

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

with open(temp_file, 'r') as infile:
  with open(outdir + '/merged_community_abundance.txt', 'w') as outfile:
    outfile.write(infile.readline())
    for line in infile:
      line=line.rstrip('\n').split('\t')
      # use the function to figure out what we want to call this line
      taxname, taxid = line[0], line[1]
      proper_name = taxid_to_lineage(taxid, taxname)
      outlist = [proper_name] + line[1:]
      outfile.write('\t'.join(outlist) + '\n')
