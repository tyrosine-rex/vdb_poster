from sklearn.manifold import MDS
import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache
def _prep_data_mds(melted, samples):
    counts = melted \
        .get("rel_count") \
        .to_frame() \
        .reset_index() \
        .pivot(columns="OTU_ID", index="SAMPLE_ID", values="rel_count")


    mds = MDS(dissimilarity="euclidean", n_components=2, normalized_stress='auto')
    pos = mds.fit(counts)

    pos_df = pd.DataFrame(pos.embedding_, index=counts.index, columns=["x", "y"])
    pos_df = pos_df \
        .merge(samples, on="SAMPLE_ID")

    pos_df["isFloor"] = pos_df.apply(lambda x: "yes" if "floor" in x["surface"] else "no", axis="columns")

    return pos_df

    
@st.cache
def plot_mds(melted, samples, color_by):
    pos_df = _prep_data_mds(melted, samples)
    fig = px.scatter(pos_df, x="x",y="y", 
        color=color_by,
        title="Multi Dimensional Scaling with Euclidean Distance Matrix between Samples"
    )
    return fig

