from os.path import exists
from toml import load
from pandas import read_csv
from sqlalchemy.types import Integer, String, Numeric
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData, Table, Column, ForeignKey

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

def init_database(db_path):
    engine = create_engine(f"sqlite:///{db_path}")
    meta = MetaData()

    taxa = Table(
        "Taxa", meta,
        Column("OTU_ID", Integer, primary_key=True), 
        Column("reign", String(64)), 
        Column("phylum", String(64)), 
        Column("class", String(64)), 
        Column("order", String(64)), 
        Column("family", String(64)), 
        Column("genus", String(64)), 
        Column("specie", String(64))
    )

    sample = Table(
        "Sample", meta,
        Column("SAMPLE_ID", String(64), primary_key=True), 
        Column("gender", String(64)), 
        Column("building", String(64)), 
        Column("floor", String(64)), 
        Column("surface", String(64))
    )

    count  = Table(
        "Count", meta,
        Column('OTU_ID', Integer, ForeignKey("Taxa.OTU_ID"), primary_key=True),
        Column('SAMPLE_ID', String(64), ForeignKey("Sample.SAMPLE_ID"), primary_key=True),
        Column("abs_val", Integer), 
        Column("norm_val", Numeric)
    )

    meta.create_all(engine)


def main():
    # load config data
    config = load(CONFIG)
    
    # read datas
    dataset, metadata = read_datas(config)

    # create dfs 
    taxa_df = load_taxa(dataset, config["phylo_col"])
    count_df = load_count(dataset, config["phylo_col"])
    sample_df = load_sample(metadata)

    # create database "sqlite"
    if not exists(config["db"]):
        init_database(config["db"])

    # populate database 
    


main()


