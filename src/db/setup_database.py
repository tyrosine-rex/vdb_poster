from os import remove
from os.path import exists
from toml import load
from pandas import read_csv
from sqlite3 import connect


CONFIG = "src/db/config.toml"


def load_taxa(df, taxa_info, taxa_colnames):
    taxa = df[taxa_info].str \
        .split(";", expand=True) \
        .replace(".__|^ ", "", regex=True) \
        .apply(lambda x:  x.str.lower()) \
        .rename_axis("OTU_ID") \
        .rename(columns={i: c for i, c in enumerate(taxa_colnames)})
    return taxa


def load_samples(df):
    samples = df.rename_axis("SAMPLE_ID") \
        .apply(lambda x: x.str.lower()) \
        .rename(columns={i: i.lower() for i in df.columns})
    return samples


def load_counts(df, taxa_info):
    counts_abs = df.drop(taxa_info, axis=1) \
        .rename_axis("OTU_ID") \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="abs_count")

    counts_rel = df.drop(taxa_info, axis=1) \
        .rename_axis("OTU_ID") \
        .divide(df.sum()) \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="rel_count")

    counts = counts_abs.merge(counts_rel, on=["OTU_ID", "SAMPLE_ID"])
    return counts


def init_database(db_path, tables):
    for sql in tables.values():
        with connect(db_path) as conn:
            conn.execute(sql)
            conn.commit()


def populate_database(db_path, taxa, counts, samples):
    with connect(db_path) as conn:
        taxa.to_sql("Taxa", conn)
        counts.to_sql("Counts", conn)
        samples.to_sql("Samples", conn)


def main():
    # load config data
    config = load(CONFIG)
    dataset_path = config["dataset"]
    metadata_path = config["metadata"]
    db_path = config["db"]
    taxa_info = config["taxa_info"]
    taxa_colnames = config["taxa_colnames"]
    tables = config["tables"]

    # read datas
    dataset = read_csv(dataset_path, sep="\t", index_col=0)
    metadata = read_csv(metadata_path, sep="\t", index_col=0)

    # create df
    taxa_df = load_taxa(dataset, taxa_info, taxa_colnames)
    counts_df = load_counts(dataset, taxa_info)
    samples_df = load_samples(metadata)

    # create database "sqlite"
    if exists(db_path):
        remove(db_path)

    init_database(db_path, tables)

    # push df to database
    populate_database(db_path, taxa=taxa_df, counts=counts_df, samples=samples_df)


if __name__ == "__main__":
    main()
