import streamlit as st
import pandas as pd


def app():
    st.title("Upload Engagement Data")

    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.session_state["uploaded_df"] = df
            st.write("### Preview")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Unable to read CSV: {e}")
    else:
        if "uploaded_df" in st.session_state:
            st.write("### Current data")
            st.dataframe(st.session_state["uploaded_df"].head())
