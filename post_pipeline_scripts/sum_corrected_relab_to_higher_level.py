import sys
import pandas as pd

db, merged_table, output, desired_rank = \
sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

# use the db to make a dictionary - taxid to (scientific) name
with open(db + '/taxonomy/names.dmp', 'r') as infile:
  taxid_to_name = {}
  for line in infile:
    line=line.rstrip('\n').split('\t')
    taxid, name, nametype = line[0], line[2], line[6]
    if nametype == 'scientific name':
      #print('here')
      taxid_to_name[taxid] = name

# go through each line in the merged table and figure out whether
# this species has info specified for the desired rank
# if so, look up the name of the associated taxid
# then add to dict of dicts
# outer keys = samples
# inner keys = taxa (of the desired rank)
# values = summed abundance

with open(merged_table, 'r') as infile:
  dict_of_dicts = {}
  header=infile.readline().rstrip('\n').split('\t')
  for line in infile:
    # header already taken care of
    line=line.rstrip('\n').split('\t')
    # does this line have the desired rank
    if desired_rank in line[0]:
      # then we care about this line!
      # get the taxid of the desired rank
      desired_rank_pos = line[0].index(desired_rank)
      # get the underscore and pipe after that
      underscore_pos = line[0][desired_rank_pos:].index('_')
      pipe_pos = line[0][desired_rank_pos:].index('|')
      taxid = line[0][desired_rank_pos:][underscore_pos+1:pipe_pos]
      # get the name!
      name = taxid_to_name[taxid]
      # add to dict of dicts
      if name in dict_of_dicts:
        for i in range(2, len(header)):
          sample = header[i]
          abundance = line[i]
          dict_of_dicts[name][sample] += float(abundance)
      else:
        dict_of_dicts[name] = {}
        for i in range(2, len(header)):
          sample = header[i]
          abundance = line[i]
          dict_of_dicts[name][sample] = float(abundance)

outdf = pd.DataFrame(dict_of_dicts).transpose()
outdf.to_csv(output, sep='\t')
