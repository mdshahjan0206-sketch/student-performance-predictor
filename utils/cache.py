"""Caching helpers to avoid recomputing expensive operations on every
Streamlit rerun (e.g. every widget interaction reruns the whole script).

Both functions are cached on the *raw bytes* of the uploaded file rather
than on the UploadedFile object itself, since that's a stable, hashable
key: re-uploading the exact same file, or simply interacting with an
unrelated widget elsewhere on the page, will hit the cache instead of
re-parsing the CSV/Excel file or recomputing summary statistics.
"""

import io
import pandas as pd
import streamlit as st

from .helpers import get_numeric_columns, get_text_category_columns


@st.cache_data(show_spinner=False)
def parse_tabular_bytes(file_bytes: bytes, file_ext: str) -> pd.DataFrame:
    """Parse CSV/Excel bytes into a DataFrame. Cached so re-running the
    page (e.g. after a filter widget changes) doesn't re-parse the file."""
    buffer = io.BytesIO(file_bytes)
    if file_ext == "csv":
        return pd.read_csv(buffer)
    return pd.read_excel(buffer)


@st.cache_data(show_spinner=False)
def compute_overview_stats(df: pd.DataFrame) -> dict:
    """Cached dataset overview stats (row/column counts, dtypes, missing
    values, duplicates). Streamlit hashes the DataFrame by content, so
    this only recomputes when the underlying data actually changes."""
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_text_category_columns(df)
    return {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


@st.cache_data(show_spinner=False)
def compute_dataset_metadata(df: pd.DataFrame) -> dict:
    """Cached per-column metadata used on the Upload Dataset page: dtypes,
    per-column missing-value counts, and the duplicate-row count.

    PERFORMANCE: `df.isnull().sum()` and `df.duplicated().sum()` are O(rows
    x cols) scans — cheap on small files, but on datasets with 100,000+
    rows this was previously recomputed from scratch on *every* Streamlit
    rerun of the Upload page (e.g. just resizing a column or interacting
    with any other widget), not only when a new file was uploaded. Caching
    on the DataFrame's content hash means it now runs once per unique
    dataset, no matter how many reruns happen afterwards.
    """
    return {
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_summary": df.isnull().sum().to_dict(),
        "duplicate_count": int(df.duplicated().sum()),
    }
