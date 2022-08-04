#filteirng merged table py prevalance
#usage: filter_by_prevalance.py <input_table> <output_table> <minimal_prevalance>
import pandas as pd
import sys

def main():
    path_in = sys.argv[1]
    path_out = sys.argv[2]
    min_prevalance = sys.argv[3]
    counts = pd.read_csv(path_in, sep="\t")
    counts['prevalance'] = (counts.iloc[: , 2:]>0).astype(int).sum(axis=1)/(counts.shape[1]-2)
    counts = counts[counts.prevalance>float(min_prevalance)]
    counts = counts.drop(columns={'prevalance'})
    counts.to_csv(path_out, sep="\t", index=False)

if __name__ == "__main__":
    main()