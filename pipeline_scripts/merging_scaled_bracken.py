import argparse
import sys
import os
import pandas as pd
import concurrent.futures


def read_scaled_table(table):
    sample_id = os.path.basename(table).split(".krak.report")[0]

    if os.path.exists(table):
        try:
            df = pd.read_csv(table, sep="\t", dtype={'taxonomy_id': 'string'})\
            .loc[:, ["taxonomy_id", "rel_taxon_abundance"]]\
            .rename(columns={"taxonomy_id": "TaxID", "rel_taxon_abundance": sample_id})\
            .set_index("TaxID")
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
        for df in executor.map(read_scaled_table, table_files):
            if df is not None:
                dfs.append(df)

    df_all = pd.concat(dfs, axis=1).fillna(0).reset_index()

    if "output" in kwargs:
        df_all.to_csv(kwargs["output"], sep="\t", index=False)
    return df_all


def taxid_to_lineages(taxid_to_rank, taxid_to_name, child_to_parent, taxid):
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


def main():
    parser = argparse.ArgumentParser("profile merger")
    parser.add_argument("--input-file", dest="input_file", nargs="+")
    parser.add_argument("--output-file", dest="output_file")
    parser.add_argument("--db", dest="db")
    parser.add_argument("--threads", dest="threads")

    args = parser.parse_args()

    # make a few helpful dictionaries
    child_to_parent = {}
    taxid_to_rank = {}
    with open(os.path.join(args.db, 'taxonomy/nodes.dmp'), 'r') as infile:
        # make a child to parent dictionary
        # and a taxid to rank dictionary
        for line in infile:
            line=line.rstrip('\n').split('\t')
            child, parent, rank = line[0], line[2], line[4]
            child_to_parent[str(child)] = parent
            taxid_to_rank[str(child)] = rank

    # also want a taxid_to_name dictionary
    # use the inspect.out file
    taxid_to_name = {}
    with open(os.path.join(args.db, 'inspect.out'), 'r') as infile:
        for line in infile:
            line=line.rstrip('\n').split('\t')
            taxid, name = line[4], line[5].strip()
            taxid_to_name[str(taxid)] = name

    # merge scaled bracken tables
    prof_df = merge_tables(args.input_file, int(args.threads))

    samples_list = list(prof_df.columns)[1:]
    headers = ["Taxon_Lineage_with_Names", "Taxon_Lineage_with_IDs"]
    prof_df[headers] = prof_df.apply(lambda x: taxid_to_lineages(taxid_to_rank, taxid_to_name, child_to_parent, x["TaxID"]), axis=1, result_type="expand")
    prof_df = prof_df.loc[:, headers + samples_list]
    prof_df.to_csv(args.output_file, sep="\t", index=False)


if __name__ == "__main__":
    main()
