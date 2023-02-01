import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache
def barplot_custom(melted, taxa, samples, phylo_choice, sample_choice):
    corr_depth = melted \
        .join(samples, on="SAMPLE_ID") \
        .get(["abs_count"]+[sample_choice]) \
        .groupby(sample_choice) \
        .sum() \
        .rename(columns={"abs_count": "corr_depth"})

    selected_count = melted \
        .join(samples.get(sample_choice), on="SAMPLE_ID") \
        .drop( ["rel_count"], axis="columns") \
        .join(taxa.fillna("").get(phylo_choice), on="OTU_ID") \
        .groupby([phylo_choice] + [sample_choice]) \
        .sum() \
        .join(corr_depth, on=sample_choice) \
        .query("abs_count != 0") \
        .reset_index()

    selected_count["rel_count"] = selected_count["abs_count"] / selected_count["corr_depth"]

    fig = px.bar(selected_count, x=sample_choice, y="rel_count", barmode="stack", color=phylo_choice) 
    
    return fig

