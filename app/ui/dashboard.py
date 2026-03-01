"""Main Streamlit dashboard for fake engagement detection."""
import streamlit as st

st.set_page_config(
    page_title="Fake Engagement Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🔍 Fake Engagement Detector")

# Upload section with helper text
st.sidebar.subheader("📤 Upload Your Data")
st.sidebar.markdown(
    """
Upload your own engagement dataset (CSV) to perform real detection.

**Required columns:**
- `timestamp` (or `time`, `date`)
- `engagement` (or `count`, `interactions`, `views`)

**Optional:** likes, comments, shares
"""
)
uploaded_file = st.sidebar.file_uploader("Choose CSV file", type=["csv"])
if uploaded_file is not None:
    import pandas as pd
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state["uploaded_df"] = df
        st.session_state["filename"] = uploaded_file.name
        st.session_state["data_source"] = "user"
        st.sidebar.success(f"✓ Loaded: {uploaded_file.name}")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")

st.sidebar.divider()

# Navigation
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Detection", "Simulation"],
    format_func=lambda x: {
        "Home": "🏠 Home",
        "Detection": "🔍 Detection",
        "Simulation": "🎲 Simulate",
    }.get(x, x),
)

st.sidebar.divider()
st.sidebar.markdown(
    """
**System Requirements:**
- FastAPI running at `localhost:8000`
- Command: `uvicorn app.api.main:app --reload`
"""
)

# Render page
if page == "Home":
    st.title("🔍 Fake Engagement Detection System")
    
    st.info(
        """
        **Demo Mode** uses a built-in synthetic engagement dataset to showcase 
        fake engagement detection capabilities.
        
        **To analyze real engagement data**, upload a CSV file in the sidebar 
        and go to the Detection page to run analysis.
        """
    )
    
    st.markdown("---")
    st.subheader("How It Works")
    st.markdown(
        """
        1. **Upload or Generate**: Provide engagement data (CSV) or use demo synthetic data
        2. **Analyze**: Run detection to compute authenticity scores
        3. **Interpret**: View anomaly timeline and behavioral triggers
        
        The system detects suspicious patterns like:
        - Sudden spikes inconsistent with normal activity
        - Off-peak engagement bursts
        - Perfect metric synchronization
        - Gradual artificial boosting
        """
    )
    
    st.markdown("---")
    st.subheader("📚 What Is Demo Mode?")
    st.markdown(
        """
        **Demo Mode** generates synthetic engagement time series that mimic 
        real behavior patterns. Use it to:
        - Explore the system without uploading data
        - Understand how detection works
        - Test different fraud patterns (burst, synchronized, off-peak, etc.)
        
        Results from demo data demonstrate the detector's capabilities but 
        are not meant for production analysis.
        """
    )
    
    st.markdown("---")
    st.subheader("📊 Real Data Analysis")
    st.markdown(
        """
        **Upload your own engagement CSV** to:
        - Analyze actual engagement patterns
        - Identify suspicious accounts or posts
        - Get authentic authenticity scores
        
        Your data is processed locally and not stored.
        """
    )

elif page == "Detection":
    from app.ui.pages import _2_detection
    _2_detection.app()
    
elif page == "Simulation":
    from app.ui.pages import _3_simulation
    _3_simulation.app()
