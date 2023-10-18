#!/usr/bin/env python


import argparse
import os
import sys
import concurrent.futures

import pandas as pd


def read_table(table):
    sample_id = os.path.basename(table).split(".krak.report")[0]

    if os.path.exists(table):
        try:
            df = pd.read_csv(table, sep="\t", names=["Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs", sample_id])\
            .set_index(["Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs"])
        except pd.errors.EmptyDataError:
            print(f"{table} is empty, pleae check")
            return None

        if not df.empty:
            return df
        else:
            return None
    else:
        print(f"{table} doesn't exists")
        return None


def merge_tables(table_files, workers, **kwargs):
    dfs = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for df in executor.map(read_table, table_files):
            if df is not None:
                dfs.append(df)

    df_all = pd.concat(dfs, axis=1).fillna(0).reset_index()

    if "output" in kwargs:
        df_all.to_csv(kwargs["output"], sep="\t", index=False)


def main():
    parser = argparse.ArgumentParser("profile merger")
    parser.add_argument("--input-file", dest="input_file", nargs="+")
    parser.add_argument("--output-file", dest="output_file")
    parser.add_argument("--threads", dest="threads")

    args = parser.parse_args()

    merge_tables(args.input_file, int(args.threads), output=args.output_file)


if __name__ == "__main__":
    main()
