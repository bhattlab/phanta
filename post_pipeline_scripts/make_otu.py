#Re-formatting merged table to OTU table
#usage: make_otu.py <input_table> <output_table>
import pandas as pd
import sys

def main():
    path_in = sys.argv[1]
    path_out = sys.argv[2]
    counts = pd.read_csv(path_in, sep="\t")
    counts = counts.drop(columns={'Taxon_Lineage_with_IDs'})
    counts = counts.rename(columns={"Taxon_Lineage_with_Names":"#OTU_ID"})
    counts.to_csv(path_out, sep="\t", index=False)

if __name__ == "__main__":
    main()