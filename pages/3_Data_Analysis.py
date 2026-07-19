import streamlit as st
import pandas as pd
from utils.eda_analyzer import (
    get_overview_stats,
    get_numeric_columns,
    get_categorical_columns,
    get_missing_summary,
    plot_histogram,
    plot_boxplot,
    plot_heatmap,
    plot_missing_values,
    plot_value_counts,
    plot_scatter
)
from utils.session_manager import get_dataset, is_dataset_uploaded
from utils.ui import inject_global_css, hero, section_title, empty_state, footer, divider, custom_radio, plotly_theme_layout, premium_table
from utils.config import CHART_TYPES

inject_global_css()

hero(
    title="Data Analysis Dashboard",
    subtitle="Slice, filter, and visualize your dataset to uncover distributions, "
             "correlations, and data quality issues before training a model.",
    badge="📊 Step 2 of 5",
    icon="📊",
)

if not is_dataset_uploaded():
    empty_state(
        "📂",
        "No dataset uploaded",
        "Please upload a dataset first to unlock the analysis dashboard.",
    )
    if st.button("← Back to Upload", type="primary"):
        st.switch_page("pages/2_Upload_Dataset.py")
else:
    dataset = get_dataset()
    df = dataset["df"]

    # === SECTION 1: Dataset Overview ===
    section_title("Dataset Overview", icon="🧮")
    stats = get_overview_stats(df)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Rows", stats['total_rows'])
    col2.metric("Total Columns", stats['total_cols'])
    col3.metric("Numeric Columns", len(stats['numeric_cols']))
    col4.metric("Categorical Columns", len(stats['categorical_cols']))
    col5.metric("Missing Values", stats['total_missing'])
    col6.metric("Duplicate Rows", stats['duplicate_rows'])

    # === SECTION 2: Distribution Analysis ===
    section_title("Distribution Analysis", icon="📉", subtitle="Explore how individual columns are distributed")

    with st.container(border=True):
        # Allow user to select column
        all_columns = list(df.columns)
        col_a, col_b = st.columns([2, 1])
        with col_a:
            selected_column = st.selectbox("Select Column", all_columns, key='dist_col')
        with col_b:
            chart_type = custom_radio("Chart Type", CHART_TYPES, key='dist_chart')

        # Render chart based on selection
        if chart_type == "Histogram":
            fig = plot_histogram(df, selected_column)
            if fig:
                fig.update_layout(**plotly_theme_layout())
                st.plotly_chart(fig, use_container_width=True, theme=None)
            else:
                st.info("ℹ️ Histogram not applicable for this column type.")
        elif chart_type == "Box Plot":
            fig = plot_boxplot(df, selected_column)
            if fig:
                fig.update_layout(**plotly_theme_layout())
                st.plotly_chart(fig, use_container_width=True, theme=None)
            else:
                st.info("ℹ️ Box plot requires a numeric column.")
        elif chart_type == "Value Counts":
            fig = plot_value_counts(df, selected_column)
            if fig:
                fig.update_layout(**plotly_theme_layout())
                st.plotly_chart(fig, use_container_width=True, theme=None)
            else:
                st.info("ℹ️ Value counts require a categorical column.")

    # === SECTION 3: Correlation Analysis ===
    section_title("Correlation Analysis", icon="🔗", subtitle="How numeric features relate to one another")
    with st.container(border=True):
        fig = plot_heatmap(df)
        if fig:
            fig.update_layout(**plotly_theme_layout())
            st.plotly_chart(fig, use_container_width=True, theme=None)
        else:
            st.info("ℹ️ Correlation heatmap requires at least two numeric columns.")

    # === SECTION 4: Missing Data Analysis ===
    section_title("Missing Data Analysis", icon="⚠️")
    with st.container(border=True):
        fig = plot_missing_values(df)
        if fig:
            fig.update_layout(**plotly_theme_layout())
            st.plotly_chart(fig, use_container_width=True, theme=None)
        else:
            st.success("✅ No missing values detected.")

    # === SECTION 5: Scatter Analysis ===
    section_title("Scatter Analysis", icon="🪁", subtitle="Compare two numeric columns")
    with st.container(border=True):
        numeric_cols = get_numeric_columns(df)
        if len(numeric_cols) < 2:
            st.info("ℹ️ Scatter plot requires at least two numeric columns.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                x_scatter = st.selectbox("X-Axis (Numeric)", numeric_cols, key='scatter_x')
            with col2:
                y_scatter = st.selectbox("Y-Axis (Numeric)", [col for col in numeric_cols if col != x_scatter], key='scatter_y')

            fig = plot_scatter(df, x_scatter, y_scatter)
            if fig:
                fig.update_layout(**plotly_theme_layout())
                st.plotly_chart(fig, use_container_width=True, theme=None)
            else:
                st.info("ℹ️ Invalid selection for scatter plot.")

    # === FILTERING PANEL ===
    # NOTE: filtering here is exploratory/visual only. It intentionally
    # does NOT call set_dataset() to write back into session state — the
    # previous version did, which meant simply opening this expander (or
    # any widget rerun on this page) permanently shrank the master
    # dataset used by Training and Prediction, with no way to undo it.
    # `filtered_df` below is a local, page-scoped view used only to
    # preview how filters would affect the analysis charts.
    filtered_df = df
    with st.expander("🔍 Apply Filters (Optional preview — does not affect Training)"):
        st.caption("These filters only preview the analysis charts below; the dataset used for training is unaffected.")

        numeric_cols = get_numeric_columns(filtered_df)
        if numeric_cols:
            col1, col2 = st.columns(2)
            with col1:
                filter_col = st.selectbox("Filter by Numeric Column", numeric_cols, key='filter_col')
            with col2:
                col_min, col_max = float(df[filter_col].min()), float(df[filter_col].max())
                min_val, max_val = st.slider(
                    "Value Range",
                    col_min, col_max, (col_min, col_max),
                    key='filter_range'
                )
            filtered_df = filtered_df[(filtered_df[filter_col] >= min_val) & (filtered_df[filter_col] <= max_val)]

        categorical_cols = get_categorical_columns(filtered_df)
        if categorical_cols:
            cat_col = st.selectbox("Filter by Category", categorical_cols, key='filter_cat')
            unique_vals = df[cat_col].dropna().unique()
            selected_cats = st.multiselect("Select Categories", unique_vals, default=unique_vals, key='filter_cats')
            if selected_cats:
                filtered_df = filtered_df[filtered_df[cat_col].isin(selected_cats)]

        if st.checkbox("Remove rows with missing values", key='remove_missing'):
            filtered_df = filtered_df.dropna()

        st.info(f"ℹ️ Preview: {len(filtered_df):,} of {len(df):,} rows match these filters.")
        if not filtered_df.equals(df):
            premium_table(filtered_df.head(50), key="filtered_preview", show_download=True, download_filename="filtered_preview.csv")

    divider()

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Upload", use_container_width=True):
            st.switch_page("pages/2_Upload_Dataset.py")
    with col2:
        if st.button("Next → Train Model", type="primary", use_container_width=True):
            st.switch_page("pages/4_Train_Model.py")

    footer()
