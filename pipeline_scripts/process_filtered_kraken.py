import sys

kraken_filtered, threshold, kraken_db = sys.argv[1], int(sys.argv[2]), sys.argv[3]

# make a dictionary that will be later useful
nodes_file = kraken_db + '/taxonomy/nodes.dmp'

def child_to_parent(nodes):
  with open(nodes, 'r') as infile:
    child_to_parent = {}
    for line in infile:
      line=line.rstrip('\n').split('\t')
      child, parent = line[0], line[2]
      child_to_parent[child] = parent
  return child_to_parent

child_parent = child_to_parent(nodes_file)

# parse filtered Kraken report, figure out whether Bracken will error
with open(kraken_filtered, 'r') as infile:
  bracken_will_fail = True
  for line in infile:
    line = line.rstrip('\n').split('\t')
    rank, assigned = line[5], int(line[1])
    if rank == 'S' and assigned >= threshold:
      bracken_will_fail = False
      break

if bracken_will_fail:

  # output an empty Bracken species report
  with open(kraken_filtered + '.bracken.temp', 'w') as outfile:
    pass

  # output an empty scaled Bracken species report
  with open(kraken_filtered + 'bracken.scaled.temp', 'w') as outfile:
    pass

  # output a Kraken-style Bracken report
  # first go through and build a dictionary from taxid to number of assigned reads
  # will subtract from ancestor nodes of removed species (that don't pass the threshold)

  with open(kraken_filtered, 'r') as infile:

    taxid_to_assigned_reads = {}

    # first line should be unclassified and we don't want this in the Bracken output
    unclass_line = infile.readline().rstrip('\n').split('\t')
    if not unclass_line[5] == 'U':
      assert unclass_line[5] == 'R' # must be root
      taxid, assigned = unclass_line[6], int(unclass_line[1])
      taxid_to_assigned_reads[taxid] = assigned

    # now go through the rest of the lines
    for line in infile:
      line=line.rstrip('\n').split('\t')
      taxid, assigned, rank = line[6], int(line[1]), line[5]

      if not rank.startswith('S'): # not a species or a strain
        taxid_to_assigned_reads[taxid] = int(assigned)

      else:
        if rank == 'S':
          if assigned < threshold:
            # will discard this species
            # i.e., don't add it to dictionary

            # also remove reads from the ancestors
            # look up the ancestors
            ancestors = set()
            child, parent = taxid, None
            while not parent == '1':
              parent = child_parent[child]
              ancestors.add(parent)
              child = parent # needed for recursion
            for ancestor in ancestors:
              taxid_to_assigned_reads[ancestor] -= assigned

          else: # keep this species
            taxid_to_assigned_reads[taxid] = int(assigned)

        else: # rank is below a species
          pass # don't care about strains

  out_fname = kraken_filtered[:kraken_filtered.rfind('.')] + '_bracken_species.filtered.temp'
  print(out_fname)
  # go through the filtered Kraken report again, look up whether each taxid is in the dictionary
  # if so, remove the 3rd and 4th elements of the line,
  # use the dictionary entry as the 1st element of the line,
  # divide the dictionary entry by root-assigned reads to get first element of line

  # so get root-assigned reads
  root_reads = taxid_to_assigned_reads['1']

  with open(kraken_filtered, 'r') as infile:
    with open(out_fname, 'w') as outfile:
      for line in infile:
        line=line.rstrip('\n').split('\t')
        taxid = line[6]
        if taxid in taxid_to_assigned_reads:
          assigned_reads = taxid_to_assigned_reads[taxid]
          if root_reads == 0:
            pc = 0.00
          else:
            pc = round(100*assigned_reads/root_reads, 2)
          line_to_output = [str(pc), str(assigned_reads), line[2]] + \
          line[5:]
          outfile.write('\t'.join(line_to_output) + '\n')
