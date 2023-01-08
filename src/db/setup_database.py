from toml import load
from pandas import read_csv, melt


CONFIG = "src/db/config.toml"

def read_datas(config):
    dat = read_csv(config["dataset"], sep="\t", index_col=0)
    met = read_csv(config["metadata"], sep="\t", index_col=0)
    return dat, met

def load_taxa(df, phylo_col):
    taxa = df[phylo_col].str \
        .split(";", expand=True) \
        .replace(".__|^ ", "", regex=True) \
        .rename_axis("OTU_ID")
    return taxa

def load_sample(df):
    sample = df.rename_axis("SAMPLE_ID")
    return sample

def load_count(df, phylo_col):
    count_abs = df.drop(phylo_col, axis=1) \
        .rename_axis("OTU_ID") \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="abs_count")

    count_rel = df.drop(phylo_col, axis=1) \
        .rename_axis("OTU_ID") \
        .divide(df.sum()) \
        .melt(ignore_index=False, var_name="SAMPLE_ID", value_name="rel_count")

    count = count_abs.merge(count_rel, on=["OTU_ID", "SAMPLE_ID"])
    return count



def main():
    config = load(CONFIG)
    
    phylo_col = config["phylo_col"]
    dataset, metadata = read_datas(config)

    taxa_df = load_taxa(dataset, phylo_col)
    sample_df = load_sample(metadata)
    count_df = load_count(dataset, phylo_col)

    


main()