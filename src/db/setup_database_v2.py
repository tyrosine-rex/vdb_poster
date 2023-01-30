from toml import load as load_toml
from pandas import read_csv


CONFIG = "src/config.toml"


def make_samples_df(metadata):
    return metadata.set_index("SampleID") \
        .rename_axis("SAMPLE_ID", axis="index") \
        .rename_axis("WC", axis="columns") \
        .apply(lambda x: x.str.lower()) \
        .rename(columns={i: i.lower() for i in metadata.columns}) \
        .astype("category")
    

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


if __name__ == "__main__":
    main()
