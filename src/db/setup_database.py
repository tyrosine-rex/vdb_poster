from toml import load as load_toml
from pandas import read_csv
from sqlite3 import connect
from os import remove
from os.path import exists


CONFIG = "src/config.toml"
TABLES = "src/db/tables.toml"


def make_samples_df(metadata):
    return metadata \
        .set_index("SampleID") \
        .rename_axis("SAMPLE_ID", axis="index") \
        .rename_axis("WC", axis="columns") \
        .apply(lambda x: x.str.lower()) \
        .rename(columns={i: i.lower() for i in metadata.columns}) \
        .astype("category") \
        .copy()
    

def make_taxa_df(dataset):
    taxa_colnames = ["reign", "phylum", "class", "_order", "family", "genus", "specie"]
    return dataset \
        .set_index("#OTU ID") \
        .rename_axis("OTU_ID", axis="index") \
        .get("ConsensusLineage") \
        .str.lower() \
        .str.split(";", expand=True) \
        .replace(".__|\(.*\)", "", regex=True) \
        .replace("^ | $", "", regex=True) \
        .replace("", None, regex=True) \
        .rename_axis("RANK", axis="columns") \
        .rename(columns={i: c for i, c in enumerate(taxa_colnames)}) \
        .astype("category") \
        .copy()


def make_counts_df(dataset):
    return dataset \
        .set_index("#OTU ID") \
        .rename_axis("OTU_ID", axis="index") \
        .rename_axis("SAMPLE_ID", axis="columns") \
        .drop("ConsensusLineage", axis="columns") \
        .astype("int64") \
        .copy()


def add_depth_column(samples, counts_abs):
    return samples \
        .merge(
            counts_abs \
                .sum(axis="index") \
                .to_frame(name="depth"),
            on="SAMPLE_ID"
        )


def make_counts_rel_df(counts_abs):
    return counts_abs \
        .divide(counts_abs.sum(), axis="columns") \
        .copy()


def make_melted_counts(counts_abs, counts_rel):
    melted_counts_abs = counts_abs \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="abs_count") \
        .reset_index() \
        .set_index(["OTU_ID", "SAMPLE_ID"]) \
        .rename_axis("COUNTS", axis="columns") \
        .copy()

    melted_counts_rel = counts_rel \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="rel_count") \
        .reset_index() \
        .set_index(["OTU_ID", "SAMPLE_ID"]) \
        .rename_axis("COUNTS", axis="columns") \
        .astype("float64") \
        .copy()

    return melted_counts_abs \
        .merge(melted_counts_rel, on=["OTU_ID", "SAMPLE_ID"]) \
        .copy()


def init_database(db_path, tables):
    if exists(db_path):
        remove(db_path)

    for sql in tables.values():
        with connect(db_path) as conn:
            conn.execute(sql)
            conn.commit()


def main():
    # load config
    config = load_toml(CONFIG)
    tables = load_toml(TABLES)

    # load path from config
    db_path = config["db"]
    dataset_path = config["dataset"]
    metadata_path = config["metadata"]
    pkl_dir = config["pickle"]

    # load csv
    dataset = read_csv(dataset_path, sep="\t")
    metadata = read_csv(metadata_path, sep="\t")

    # make df
    samples = make_samples_df(metadata)
    taxa = make_taxa_df(dataset)
    counts_abs = make_counts_df(dataset)
    counts_rel = make_counts_rel_df(counts_abs)
    melted_counts = make_melted_counts(counts_abs, counts_rel)
    samples = add_depth_column(samples, counts_abs)

    # export df to pickle format
    samples.to_pickle(f"{pkl_dir}/samples.pkl")
    taxa.to_pickle(f"{pkl_dir}/taxa.pkl")
    counts_abs.to_pickle(f"{pkl_dir}/counts_abs.pkl")
    counts_rel.to_pickle(f"{pkl_dir}/counts_rel.pkl")
    melted_counts.to_pickle(f"{pkl_dir}/melted_counts.pkl")

    # init database
    init_database(db_path, tables)

    # populate database
    with connect(db_path) as conn: 
        taxa.to_sql("Taxa", conn, if_exists="append") # append to keep constraints from 'init_database()'
        melted_counts.to_sql("Counts", conn, if_exists="append")
        samples.to_sql("Samples", conn, if_exists="append")
        conn.commit()


if __name__ == "__main__":
    main()