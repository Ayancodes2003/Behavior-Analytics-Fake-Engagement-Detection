"""Upload page for CSV engagement data."""
import streamlit as st
import pandas as pd


def app():
    st.title("💾 Upload Engagement Data")
    
    st.write("""
    Upload a CSV file with engagement time series. Minimum required columns:
    - **timestamp**: Date/time of engagement record
    - **views** (or **engagement_count**): Number of views/impressions
    
    Optional columns: likes, comments, shares
    """)
    
    uploaded = st.file_uploader("Choose CSV file", type=["csv"])

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.success(f"✓ Loaded {len(df)} records")
            st.write("**Preview:**")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Store in session state for other pages
            st.session_state["uploaded_df"] = df
            st.session_state["filename"] = uploaded.name
            
            st.info(f"Ready to analyze! Go to the **Detection** page.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

