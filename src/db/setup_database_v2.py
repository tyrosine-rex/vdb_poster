from toml import load as load_toml
from pandas import read_csv


CONFIG = "src/config.toml"


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
    taxa_colnames = ["reign", "phylum", "class", "order", "family", "genus", "specie"]
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


def make_counts_rel_df(counts):
    return counts \
        .divide(counts.sum(), axis="columns") \
        .copy()


def main():
    # load config
    config = load_toml(CONFIG)
    
    # load path from config
    db_path = config["db2"]
    dataset_path = config["dataset"]
    metadata_path = config["metadata"]

    # load csv
    dataset = read_csv(dataset_path, sep="\t")
    metadata = read_csv(metadata_path, sep="\t")

    samples = make_samples_df(metadata)
    taxa = make_taxa_df(dataset)
    counts = make_counts_df(dataset)
    
    counts_rel = make_counts_rel_df(counts)


if __name__ == "__main__":
    main()
