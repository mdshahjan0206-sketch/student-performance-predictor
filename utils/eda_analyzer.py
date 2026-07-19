import pandas as pd
import plotly.express as px
import streamlit as st

from .config import COLOR_PALETTE
from .cache import compute_overview_stats
from .helpers import get_numeric_columns as _get_numeric_columns, get_text_category_columns

# Shared layout overrides so every chart here renders on a transparent
# background with brand-matching text, regardless of which browser/CSS
# environment it's viewed in (see the DEPLOYMENT THEME LOCK section in
# assets/css/style.css for why this matters on Streamlit Cloud). Kept as a
# local constant rather than importing from utils.ui so this analysis module
# stays free of any dependency on the presentation layer.
_PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1F2937", family="Inter, 'Plus Jakarta Sans', sans-serif"),
)


def get_overview_stats(df):
    """Return dataset overview statistics (cached; recomputes only when
    the underlying data actually changes, not on every widget rerun)."""
    return compute_overview_stats(df)


def get_numeric_columns(df):
    """Return list of numeric columns."""
    return _get_numeric_columns(df)


def get_categorical_columns(df):
    """Return list of categorical columns."""
    return get_text_category_columns(df)


def get_missing_summary(df):
    """Return series of missing values per column."""
    return df.isnull().sum()


@st.cache_data(show_spinner=False)
def plot_histogram(df, column):
    """Generate histogram. Cached on (df content, column) so re-rendering
    the same chart after an unrelated widget interaction elsewhere on the
    page reuses the previous figure instead of rebuilding it."""
    try:
        fig = px.histogram(
            df,
            x=column,
            title=f"Distribution of {column}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None

@st.cache_data(show_spinner=False)
def plot_boxplot(df, column):
    """Cached — see plot_histogram."""
    try:
        if column not in get_numeric_columns(df):
            return None

        fig = px.box(
            df,
            y=column,
            title=f"Box Plot of {column}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None


@st.cache_data(show_spinner=False)
def plot_heatmap(df):
    """Cached — correlation on wide/tall datasets is the most expensive
    chart here, so this is the biggest win from caching."""
    try:

        numeric = df[get_numeric_columns(df)]

        if numeric.shape[1] < 2:
            return None

        corr = numeric.corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap"
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None


@st.cache_data(show_spinner=False)
def plot_missing_values(df):
    """Cached — see plot_histogram."""
    try:

        missing = df.isnull().sum()

        missing = missing[missing > 0]

        if missing.empty:
            return None

        missing_df = missing.reset_index()

        missing_df.columns = ["Column", "Missing"]

        fig = px.bar(
            missing_df,
            x="Column",
            y="Missing",
            title="Missing Values",
            color_discrete_sequence=[COLOR_PALETTE[4]]  # danger color for missing-data bars
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None


@st.cache_data(show_spinner=False)
def plot_value_counts(df, column):
    """Cached — see plot_histogram."""
    try:

        if column not in get_categorical_columns(df):
            return None

        value_counts = (
            df[column]
            .value_counts()
            .rename_axis(column)
            .reset_index(name="Count")
        )

        fig = px.bar(
            value_counts,
            x=column,
            y="Count",
            title=f"Value Counts of {column}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None

@st.cache_data(show_spinner=False)
def plot_scatter(df, x_col, y_col):
    """Cached — see plot_histogram."""
    try:

        if x_col == y_col:
            return None

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=f"{x_col} vs {y_col}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig.update_layout(**_PLOTLY_LAYOUT)

        return fig

    except Exception as e:
        print(e)
        return None