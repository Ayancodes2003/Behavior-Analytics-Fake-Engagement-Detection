import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.detector_service import detect_from_dataframe


def app():
    st.title("Detection Results")

    df = st.session_state.get("uploaded_df")
    if df is None:
        st.info("Please upload a dataset on the Upload page first.")
        return

    if st.button("Run Detection"):
        try:
            result = detect_from_dataframe(df)
            st.session_state["detection_result"] = result
        except Exception as e:
            st.error(f"Detection failed: {e}")
            return

    result = st.session_state.get("detection_result")
    if result:
        st.write("### Summary")
        st.write(f"Authenticity: {result['authenticity_score']:.2f}")
        st.write(f"Bot probability: {result['bot_probability']:.2f}")
        st.write("Top triggers:", result.get("top_behavioral_triggers", []))

        # plot time series and anomalies
        records = result.get("per_row_scores", [])
        if records:
            plot_df = pd.DataFrame(records)
            fig = px.line(plot_df, x="timestamp", y="views", title="Engagement over time")
            if "anomaly_score" in plot_df.columns:
                # mark anomalies with scatter
                mask = plot_df["anomaly_score"] > plot_df["anomaly_score"].mean()
                fig.add_scatter(
                    x=plot_df.loc[mask, "timestamp"],
                    y=plot_df.loc[mask, "views"],
                    mode="markers",
                    marker=dict(color="red", size=8),
                    name="Anomaly",
                )
            st.plotly_chart(fig, use_container_width=True)
