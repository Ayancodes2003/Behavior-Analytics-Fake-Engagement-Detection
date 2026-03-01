"""Detection results page."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta


def app():
    st.title("🔍 Detect Fake Engagement")
    
    # Determine data source
    df = st.session_state.get("uploaded_df")
    data_source = st.session_state.get("data_source", None)
    filename = st.session_state.get("filename", "")
    
    # Show badge and instructions
    if df is not None and data_source == "user":
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"Analyzing: **{filename}** ({len(df)} records)")
        with col2:
            st.metric("📊", "User Data")
    elif df is not None and data_source == "demo":
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"**{filename}** ({len(df)} records)")
        with col2:
            st.metric("🎲", "Demo Data")
    else:
        st.warning(
            "⚠️ **No data loaded.** Please either:\n"
            "1. Upload a CSV file in the sidebar, OR\n"
            "2. Use the **Simulate** page to generate demo data"
        )
        st.info(
            "**Demo Mode**: Generate synthetic engagement data to explore the detector "
            "without uploading real data."
        )
        return

    if st.button("🚀 Run Detection", use_container_width=True):
        with st.spinner("Analyzing engagement patterns..."):
            try:
                # Send to API
                csv_text = df.to_csv(index=False)
                resp = requests.post(
                    "http://localhost:8000/detect",
                    data={"csv_text": csv_text},
                    timeout=30,
                )
                
                if resp.status_code == 200:
                    result = resp.json()
                    
                    # Display data source badge in results
                    st.divider()
                    if data_source == "demo":
                        st.info("**Demo Results** — Using synthetic behavioral engagement data")
                    else:
                        st.success("**User Dataset Results** — Analysis of uploaded engagement data")
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        auth = result.get("authenticity_score", 0)
                        st.metric("🎯 Authenticity", f"{auth:.1f}%")
                    with col2:
                        bot = result.get("bot_probability", 0)
                        st.metric("🤖 Bot Probability", f"{bot:.1%}")
                    with col3:
                        anom = result.get("anomaly_score", 0)
                        st.metric("⚠️ Anomaly Score", f"{anom:.3f}")
                    
                    st.divider()
                    
                    # Behavioral triggers
                    triggers = result.get("top_behavioral_triggers", [])
                    if triggers:
                        st.subheader("🔴 Top Behavioral Triggers")
                        st.markdown(
                            "**Features most indicative of suspected fraud:**"
                        )
                        for i, trigger in enumerate(triggers, 1):
                            st.write(f"{i}. **{trigger}**")
                    else:
                        st.info("No strong behavioral triggers detected.")
                    
                    st.divider()
                    
                    # Plot timeline with anomaly markers
                    st.subheader("📈 Engagement Timeline with Anomaly Scores")
                    per_row = pd.DataFrame(result.get("per_row_scores", []))
                    if not per_row.empty:
                        per_row["timestamp"] = pd.to_datetime(per_row["timestamp"])
                        
                        # Find engagement column
                        eng_col = None
                        for col in ["views", "engagement", "engagement_count", "count"]:
                            if col in per_row.columns:
                                eng_col = col
                                break
                        if eng_col is None:
                            eng_col = per_row.columns[1] if len(per_row.columns) > 1 else "views"
                        
                        fig = px.line(
                            per_row,
                            x="timestamp",
                            y=eng_col,
                            title="Engagement over Time",
                            labels={eng_col: "Engagement"},
                        )
                        
                        # Highlight suspicious periods (anomaly_score > mean)
                        mean_anom = per_row["anomaly_score"].mean()
                        suspicious = per_row[per_row["anomaly_score"] > mean_anom]
                        if not suspicious.empty:
                            fig.add_trace(
                                go.Scatter(
                                    x=suspicious["timestamp"],
                                    y=suspicious[eng_col],
                                    mode="markers",
                                    name="Anomaly (High Score)",
                                    marker=dict(
                                        size=10,
                                        color="red",
                                        symbol="star",
                                    ),
                                )
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.caption(
                            "Red stars indicate timestamps with anomaly scores above the mean, "
                            "suggesting suspicious activity."
                        )
                else:
                    st.error(f"❌ Detection failed: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "⚠️ **Cannot connect to API.** \n\n"
                    "Start FastAPI in a terminal with:\n"
                    "`uvicorn app.api.main:app --reload`"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
