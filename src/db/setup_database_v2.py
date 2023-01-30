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
        .astype("uint16") \
        .copy()


def make_counts_rel_df(counts_abs):
    return counts_abs \
        .divide(counts_abs.sum(), axis="columns") \
        .copy()


def make_melted_counts(counts_abs, counts_rel):
    melted_counts_abs = counts_abs \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="count_abs") \
        .reset_index() \
        .set_index(["OTU_ID", "SAMPLE_ID"]) \
        .rename_axis("COUNTS", axis="columns")

    melted_counts_rel = counts_rel \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="count_rel") \
        .reset_index() \
        .set_index(["OTU_ID", "SAMPLE_ID"]) \
        .rename_axis("COUNTS", axis="columns")

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
    db_path = config["db2"]
    dataset_path = config["dataset"]
    metadata_path = config["metadata"]

    # load csv
    dataset = read_csv(dataset_path, sep="\t")
    metadata = read_csv(metadata_path, sep="\t")

    # make df
    samples = make_samples_df(metadata)
    taxa = make_taxa_df(dataset)
    counts_abs = make_counts_df(dataset)
    counts_rel = make_counts_rel_df(counts_abs)
    melted_counts = make_melted_counts(counts_abs, counts_rel)

    # init database
    init_database(db_path, tables)



if __name__ == "__main__":
    main()
