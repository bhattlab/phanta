import pandas as pd
import glob, os, sys
from Bio import SeqIO

def get_taxid(name):
    # get taxid from provided fasta file header
    lst_pipe = name.rfind("|")
    tax_start = name.rfind("kraken:taxid|")+12
    next_pipe = name.find("|", tax_start+1)
    if lst_pipe>tax_start:
        taxid=name[tax_start+1:next_pipe]
    else:
        taxid=name[tax_start+1:]
    return taxid

def make_dicts(nodes_file):
  with open(nodes_file, 'r') as infile:
    # make a child to parent dictionary
    # and a taxid to rank dictionary
    child_to_parent = {}
    taxid_to_rank = {}
    for line in infile:
      line=line.rstrip('\n').split('\t')
      child, parent, rank = line[0], line[2], line[4]
      child_to_parent[child] = parent
      taxid_to_rank[child] = rank
  return child_to_parent, taxid_to_rank

def taxid_to_species_taxid(taxid, child_parent, taxid_rank):
  # look up the specific taxid,
  # build the lineage using the dictionaries
  # stop at species and retrn the taxid
  lineage = [[taxid, taxid_rank[taxid]]]
  if taxid_rank[taxid] == 'species':
    return taxid
  child, parent = taxid, None
  if child == '0':
    return 'unclassified'
  while not parent == '1':
    # print(child, parent)
    # look up child, add to lineage
    parent = child_parent[child]
    rank = taxid_rank[parent]
    lineage.append([parent, rank])
    if rank == 'species':
      return parent
    child = parent # needed for recursion
  return 'error - taxid above species'

def genome_length(FastaFile):
    print("working on", FastaFile)
    d=[]
    #FastaFile = open(path, 'rU')
    for rec in SeqIO.parse(FastaFile, 'fasta'):
        name = rec.id
        taxid = get_taxid(name)
        seq = rec.seq
        seqLen = len(rec)
        d.append(
        {
            'Record_name': name,
            'Taxonomy': taxid,
            'Length': seqLen,
        }
        )
    #FastaFile.close()
    df =  pd.DataFrame(d)
    # return the sum of genome lengths for all genomes falling under this taxid
    return df.groupby('Taxonomy').sum()

def main():
    kraken_lib = sys.argv[1]
    files = glob.glob(os.path.join(kraken_lib+"/library/**", "*.fna"), recursive=True)
    dfs = [genome_length(f) for f in files]
    lengths = pd.concat(dfs)
    child_parent, taxid_rank = make_dicts(kraken_lib + '/taxonomy/nodes.dmp')
    lengths['Taxonomy']= lengths.index
    lengths['species_level_taxa'] = lengths.apply(lambda x: taxid_to_species_taxid(str(x['Taxonomy']), child_parent, taxid_rank ), axis=1)
    # now we have a data frame with taxid, length of genome, species taxid
    lengths.to_csv(kraken_lib+"/library/taxa_genome_size.txt", sep="\t")
    a=lengths.groupby('species_level_taxa')['Length'].apply(list).rename("lengths")
    b=lengths.groupby('species_level_taxa')['Length'].max().rename("max")
    c=lengths.groupby('species_level_taxa')['Length'].mean().rename("mean")
    d=lengths.groupby('species_level_taxa')['Length'].median().rename("median")
    e=lengths.groupby('species_level_taxa')['Length'].count().rename("count")
    f=lengths.groupby('species_level_taxa')['Taxonomy'].apply(list).rename("taxa_list")
    length_per_species = pd.concat([b,c,d,e,a,f],axis=1)
    length_per_species.to_csv(kraken_lib+"/library/species_genome_size.txt", sep="\t")


if __name__ == "__main__":
    main()
