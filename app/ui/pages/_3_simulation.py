import streamlit as st
import pandas as pd
import plotly.express as px
from app.services import detector_service
from core import simulation, injection


def app():
    st.title("Simulation")
    st.sidebar.subheader("Parameters")
    start_date = st.sidebar.date_input("Start date")
    length_days = st.sidebar.number_input("Length (days)", min_value=1, value=30)
    frequency = st.sidebar.selectbox("Frequency", ["H", "D"])
    video_id = st.sidebar.text_input("Video ID", "sim_001")
    fake = st.sidebar.checkbox("Inject fake pattern?", value=False)
    fake_pattern = st.sidebar.selectbox("Fake pattern", ["burst", "synchronized", "off_peak", "perfect_correlation"])

    if st.button("Generate"):
        if fake:
            df = injection.inject_fake_engagement(
                start_date=start_date,
                length_days=length_days,
                frequency=frequency,
                video_id=video_id,
                fake_pattern=fake_pattern,
            )
        else:
            df = simulation.simulate_engagement(
                start_date=start_date,
                length_days=length_days,
                frequency=frequency,
                video_id=video_id,
            )
        st.session_state["simulated_df"] = df
        st.write(df.head())

    sim_df = st.session_state.get("simulated_df")
    if sim_df is not None:
        fig = px.line(sim_df, x="timestamp", y="views", title="Simulated engagement")
        st.plotly_chart(fig, use_container_width=True)
