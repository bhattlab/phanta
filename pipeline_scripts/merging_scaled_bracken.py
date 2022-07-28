import sys

db, temp_file, outdir = sys.argv[1], sys.argv[2], sys.argv[3]

# make a few helpful dictionaries

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

# also want a taxid_to_name dictionary
# use the inspect.out file

with open(db + '/inspect.out', 'r') as infile:
  taxid_to_name = {}
  for line in infile:
    line=line.rstrip('\n').split('\t')
    taxid, name = line[4], line[5].strip()
    taxid_to_name[taxid] = name

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
  return lineage_names, lineage_taxids

with open(temp_file, 'r') as infile:
  with open(outdir + '/relative_taxonomic_abundance.txt', 'w') as outfile:
    # first fix the header
    orig_header = infile.readline().rstrip('\n').split('\t')
    new_header = '\t'.join(['Taxon_Lineage_with_Names', 'Taxon_Lineage_with_IDs'] + orig_header[1:]) + '\n'
    outfile.write(new_header)
    for line in infile:
      line=line.rstrip('\n').split('\t')
      # use the function to figure out what we want to call this line
      taxid = line[0]
      lin_names, lin_ids = taxid_to_lineages(taxid)
      outlist = [lin_names, lin_ids] + line[1:]
      outfile.write('\t'.join(outlist) + '\n')
