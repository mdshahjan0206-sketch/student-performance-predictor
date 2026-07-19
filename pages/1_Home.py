import streamlit as st
from utils.ui import inject_global_css, hero, section_title, feature_card_html, stat_html, footer

inject_global_css()

hero(
    title="Welcome to EduPredict AI",
    subtitle="Upload student data, explore it visually, train machine learning models, "
             "and generate accurate performance predictions — all in one elegant workspace.",
    badge="🎓 Home",
    icon="👋",
)

# Animated stat strip
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(stat_html("6", "Guided Steps"), unsafe_allow_html=True)
with s2:
    st.markdown(stat_html("3+", "ML Model Types"), unsafe_allow_html=True)
with s3:
    st.markdown(stat_html("100%", "In-Browser & Private"), unsafe_allow_html=True)
with s4:
    st.markdown(stat_html("∞", "Datasets Supported"), unsafe_allow_html=True)

section_title("How it works", icon="🧭", subtitle="A simple, guided workflow from raw data to prediction")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        feature_card_html("📂", "1. Upload Dataset", "Bring your own CSV or Excel file of student records. We validate and summarize it instantly."),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        feature_card_html("📊", "2. Explore & Analyze", "Interactive charts reveal distributions, correlations, and missing data at a glance."),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        feature_card_html("🤖", "3. Train a Model", "Pick a target column and let our pipeline train and evaluate a model in seconds."),
        unsafe_allow_html=True,
    )

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(
        feature_card_html("🔮", "4. Predict", "Score a single student or an entire batch, with confidence scores included."),
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        feature_card_html("📥", "5. Export Results", "Download prediction results as CSV for reporting or further analysis."),
        unsafe_allow_html=True,
    )
with c6:
    st.markdown(
        feature_card_html("🔒", "6. Stay in Control", "Nothing leaves your session — all processing happens locally in this app."),
        unsafe_allow_html=True,
    )

section_title("Ready when you are", icon="🚀", subtitle="Jump straight into the workflow")

nav1, nav2 = st.columns(2)
with nav1:
    if st.button("📂 Upload Your Dataset", type="primary", use_container_width=True):
        st.switch_page("pages/2_Upload_Dataset.py")
with nav2:
    if st.button("ℹ️ Learn More About This App", use_container_width=True):
        st.switch_page("pages/6_About.py")

footer()
