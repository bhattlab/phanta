#filteirng for virus-bacteria correlations by significance
#usage:filter_interkingdom.py <pref_correl.txt> <pref_pvalues.tsv> <minimal p-value>  <interkingdom_correlations.txt>
import pandas as pd
import numpy as np
import sys

def main():
    minimal_p = float(sys.argv[3])
    path_corr = sys.argv[1]
    path_p = sys.argv[2]
    path_out =  sys.argv[4]
    corr = pd.read_csv(path_corr, sep="\t", index_col=0)
    pvals = pd.read_csv(path_p, sep="\t", index_col=0)
    corr[pvals>float(minimal_p)]=np.nan
    inter_kingdom = corr.loc[corr.index.str.contains("superkingdom_Viruses"), corr.columns.str.contains("superkingdom_Bacteria")]
    inter_kingdom.to_csv(path_out, sep="\t")
    

if __name__ == "__main__":
    main()