import streamlit as st
import textwrap
from utils.ui import inject_global_css, hero, section_title, feature_card_html, footer, developer_card

inject_global_css()

hero(
    title="About EduPredict AI",
    subtitle="A premium, end-to-end machine learning workspace for predicting "
             "student academic performance.",
    badge="ℹ️ About",
    icon="ℹ️",
)

st.markdown(
    textwrap.dedent(
        """
        <div class="pp-card">
            <p style="font-size:1.02rem; color:#6B7280; margin:0; line-height:1.7;">
                This application predicts student performance using machine learning.
                Built as a portfolio project with Streamlit and scikit-learn, it is
                designed for modern, responsive, and production-grade use.
            </p>
        </div>
        """
    ).strip(),
    unsafe_allow_html=True,
)

section_title("Mission & Vision", icon="🎯")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        feature_card_html(
            "🎯", "Our Mission",
            "Make data-driven insight into student outcomes accessible to educators, "
            "researchers, and institutions — without requiring a data science background."
        ),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        feature_card_html(
            "🔭", "Our Vision",
            "A world where every learner benefits from early, transparent, and "
            "actionable performance insight, powered by responsible AI."
        ),
        unsafe_allow_html=True,
    )

section_title("Technology Stack", icon="🛠️")
t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(feature_card_html("🎈", "Streamlit", "Interactive multi-page web app framework."), unsafe_allow_html=True)
with t2:
    st.markdown(feature_card_html("🐼", "Pandas", "Data loading, cleaning, and transformation."), unsafe_allow_html=True)
with t3:
    st.markdown(feature_card_html("🧠", "scikit-learn", "Model training, evaluation, and pipelines."), unsafe_allow_html=True)
with t4:
    st.markdown(feature_card_html("📈", "Plotly", "Interactive, publication-quality charts."), unsafe_allow_html=True)

section_title("Architecture", icon="🏗️", subtitle="A simple, guided pipeline from raw data to prediction")
st.markdown(
    textwrap.dedent(
        """
        <div class="pp-card">
            <p style="color:#6B7280; margin:0; line-height:1.8;">
                <strong>Upload</strong> → <strong>Analyze</strong> → <strong>Train</strong> → <strong>Predict</strong><br/>
                Each stage hands off state through a shared session manager, so your dataset
                and trained model travel with you across every page of the app.
            </p>
        </div>
        """
    ).strip(),
    unsafe_allow_html=True,
)

section_title("Timeline", icon="🗓️")
st.markdown(
    textwrap.dedent(
        """
        <div class="pp-card">
            <p style="color:#6B7280; margin:0 0 0.6rem 0;"><strong>Milestone 1</strong> — Dataset upload & validation</p>
            <p style="color:#6B7280; margin:0 0 0.6rem 0;"><strong>Milestone 2</strong> — Exploratory data analysis dashboard</p>
            <p style="color:#6B7280; margin:0 0 0.6rem 0;"><strong>Milestone 3</strong> — Model training & evaluation</p>
            <p style="color:#6B7280; margin:0;"><strong>Milestone 4</strong> — Single & batch prediction</p>
        </div>
        """
    ).strip(),
    unsafe_allow_html=True,
)

section_title("Developer", icon="👨‍💻", subtitle="The mind behind this project")
developer_card()

section_title("Contact", icon="✉️")
st.markdown(
    textwrap.dedent(
        """
        <div class="pp-card" style="text-align:center;">
            <p style="color:#6B7280; margin:0;">
                Questions or feedback? Reach out via the project repository or your course instructor.
            </p>
        </div>
        """
    ).strip(),
    unsafe_allow_html=True,
)

footer()
