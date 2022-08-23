import sys
import pandas as pd

db, merged_table, output, desired_rank = \
sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

# go through each line in the merged table and figure out whether
# this species has info specified for the desired rank
# if so, cut both versions of the ID down to the desired rank

# add to a dict of dicts
# outer keys = taxa (of the desired rank) - using the 'names' identifier
# inner keys = samples
# values = summed abundance

# also add to another dictionary
# mapping 'names' identifiers to 'taxids' identifiers

dict_of_dicts, names_to_taxids = {}, {}

with open(merged_table, 'r') as infile:
  header=infile.readline().rstrip('\n').split('\t')
  for line in infile:
    # header already taken care of
    line=line.rstrip('\n').split('\t')
    id_names, id_taxids = line[0], line[1]
    if "|"+desired_rank in id_names:
   
      # then we care about this line!

      # cut id_names and id_taxids down to just the desired rank
      # need to get a "stopping point"
      rank_pos_names = id_names.index(desired_rank)
      pipe_pos_names = id_names[rank_pos_names:].index('|')
      id_names_short = id_names[:rank_pos_names+pipe_pos_names]

      rank_pos_taxids = id_taxids.index(desired_rank)
      pipe_pos_taxids = id_taxids[rank_pos_taxids:].index('|')
      id_taxids_short = id_taxids[:rank_pos_taxids+pipe_pos_taxids]

      # add to names_to_taxids
      names_to_taxids[id_names_short] = id_taxids_short

      # add to dict_of_dicts
      if id_names_short in dict_of_dicts:
        for i in range(2, len(header)):
          sample = header[i]
          abundance = line[i]
          if abundance == 'NA':
            dict_of_dicts[id_names_short][sample] += 0
          else:
            dict_of_dicts[id_names_short][sample] += float(abundance)
      else:
        dict_of_dicts[id_names_short] = {}
        for i in range(2, len(header)):
          sample = header[i]
          abundance = line[i]
          if abundance == 'NA':
            dict_of_dicts[id_names_short][sample] = 0
          else:
            dict_of_dicts[id_names_short][sample] = float(abundance)

outdf = pd.DataFrame(dict_of_dicts).transpose()
# make the rownames into a column
outdf.index.name = 'Taxon_Lineage_with_Names'
outdf.reset_index(inplace=True)

# merge with IDs
mapping = pd.DataFrame.from_dict(names_to_taxids, orient='index')
# make the rownames into a column
mapping.index.name = 'Taxon_Lineage_with_Names'
mapping.reset_index(inplace=True)
mapping = mapping.rename(columns={0: "Taxon_Lineage_with_IDs"})

# merge, reorder, output
outdf = outdf.merge(mapping, on = "Taxon_Lineage_with_Names")
outdf.insert(1, "Taxon_Lineage_with_IDs", outdf.pop("Taxon_Lineage_with_IDs"))
outdf.to_csv(output, index=False, sep='\t')
