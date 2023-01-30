from toml import load as load_toml
from pandas import read_csv


CONFIG = "src/config.toml"


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



if __name__ == "__main__":
    main()
