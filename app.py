import streamlit as st
import textwrap

st.set_page_config(page_title="Student Performance Predictor", page_icon="🎓", layout="wide")

from utils.ui import inject_global_css, hero, footer, sidebar_footer, splash_credit

inject_global_css()
sidebar_footer()

hero(
    title="EduPredict AI",
    subtitle="A premium, end-to-end machine learning workspace for exploring, training, "
             "and predicting student academic performance.",
    badge="🚀 AI-Powered Analytics Platform",
    icon="🎓",
)

st.markdown(
    textwrap.dedent(
        """
        <div class="pp-card" style="text-align:center; padding:2.4rem;">
            <h3 style="margin-bottom:0.5rem;">Use the sidebar to get started</h3>
            <p style="color:var(--text-muted); margin-bottom:0;">
                Head to <strong>Home</strong> for an overview, or jump straight to
                <strong>Upload Dataset</strong> to begin analyzing your data.
            </p>
        </div>
        """
    ).strip(),
    unsafe_allow_html=True,
)

splash_credit()

footer()
