"""Simulation page for generating synthetic engagement demo data."""
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta


def app():
    st.title("🎲 Generate Demo Engagement Data")
    
    st.info(
        "**Demo Mode** generates synthetic engagement time series. Use this to explore "
        "the detector without uploading real data. Results are **not** for production analysis."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
        )
    with col2:
        length_days = st.slider(
            "Duration (days)",
            min_value=1,
            max_value=100,
            value=30,
        )
    
    col1, col2 = st.columns(2)
    with col1:
        frequency = st.selectbox(
            "Frequency",
            ["H", "D"],
            format_func=lambda x: "Hourly" if x == "H" else "Daily"
        )
    with col2:
        video_id = st.text_input("Series ID", value="demo_001")
    
    st.divider()
    st.subheader("Engagement Type")
    
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        fake = st.checkbox("Include fraud pattern?", value=False)
    with col2:
        if fake:
            fake_pattern = st.selectbox(
                "Fraud type",
                ["burst", "synchronized", "off_peak", "perfect_correlation"],
                help="Type of fake engagement to inject",
            )
        else:
            fake_pattern = "burst"
    
    st.markdown("---")
    
    if st.button("🚀 Generate Demo Data", use_container_width=True):
        with st.spinner("Generating synthetic data..."):
            try:
                params = {
                    "start_date": start_date.isoformat(),
                    "length_days": length_days,
                    "frequency": frequency,
                    "video_id": video_id,
                    "fake": fake,
                    "fake_pattern": fake_pattern,
                }
                
                resp = requests.post(
                    "http://localhost:8000/simulate",
                    params=params,
                    timeout=30,
                )
                
                if resp.status_code == 200:
                    data = pd.DataFrame(resp.json())
                    st.success(f"✓ Generated {len(data)} records")
                    
                    # Store for detection page with demo flag
                    st.session_state["uploaded_df"] = data
                    st.session_state["filename"] = (
                        f"{video_id} (Fake)" if fake else f"{video_id} (Normal)"
                    )
                    st.session_state["data_source"] = "demo"
                    
                    st.dataframe(data.head(10), use_container_width=True)
                    
                    # Plot synthetic data
                    st.subheader("📊 Generated Time Series")
                    data["timestamp"] = pd.to_datetime(data["timestamp"])
                    
                    fig = px.line(
                        data,
                        x="timestamp",
                        y="views",
                        title=f"Synthetic Engagement - {video_id}",
                        color_discrete_sequence=["#FF0000" if fake else "#00AA00"],
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data characteristics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Mean Views", f"{data['views'].mean():.0f}")
                    with col2:
                        st.metric("Max Views", f"{data['views'].max():.0f}")
                    with col3:
                        st.metric("Std Dev", f"{data['views'].std():.0f}")
                    
                    st.divider()
                    
                    st.info(
                        "💡 **Ready for analysis!** Go to the **Detection** page to analyze "
                        "this demo data. Remember: these results demonstrate detector capabilities "
                        "on synthetic data only."
                    )
                    
                    if fake:
                        st.warning(
                            f"⚠️ This dataset includes **{fake_pattern}** fraud injection. "
                            "The detector should flag anomalies in the affected periods."
                        )
                else:
                    st.error(f"❌ Simulation failed: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "⚠️ **Cannot connect to API.** \n\n"
                    "Start FastAPI with:\n"
                    "`uvicorn app.api.main:app --reload`"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
