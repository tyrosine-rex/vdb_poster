from sqlite3 import connect
from pandas import read_sql


def data_loader(db_path):
    with connect(db_path) as conn: 
        taxa = read_sql("select * from Taxa", conn)
        samples = read_sql("select * from Samples", conn)
        melted = read_sql("select * from Counts", conn)

    melted = melted.set_index(["OTU_ID", "SAMPLE_ID"])
    samples = samples.set_index("SAMPLE_ID")
    taxa = taxa.fillna("").set_index("OTU_ID")

    return melted, samples, taxa