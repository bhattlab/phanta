import sys

kraken_filtered, threshold, kraken_db = \
sys.argv[1], int(sys.argv[2]), sys.argv[3]

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

  # output an empty Kraken-style Bracken report
  out_fname = kraken_filtered[:kraken_filtered.rfind('.')] + '_bracken_species.filtered.temp'
  with open(out_fname, 'w') as outfile:
    pass

  # output an empty scaled Bracken species report
  with open(kraken_filtered + '.bracken.scaled.temp', 'w') as outfile:
    pass
