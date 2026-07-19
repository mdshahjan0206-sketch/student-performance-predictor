import pandas as pd
import streamlit as st
from .cache import parse_tabular_bytes, compute_dataset_metadata
from .helpers import detect_target_candidates


def load_dataset(uploaded_file):
    """
    Load dataset from uploaded file (CSV or Excel).
    Returns: dict with metadata and DataFrame or None if invalid.
    """
    if uploaded_file is None:
        return None

    try:
        file_bytes = uploaded_file.getvalue()
        file_size = len(file_bytes)
        file_name = uploaded_file.name
        file_ext = file_name.lower().split('.')[-1]

        # Validate file type
        if file_ext not in ['csv', 'xlsx']:
            st.error("❌ Unsupported file format. Please upload a .csv or .xlsx file.")
            return None

        # Load data (cached on file bytes so re-running the page doesn't
        # re-parse the same file on every rerun)
        df = parse_tabular_bytes(file_bytes, file_ext)

        # Validate empty file
        if df.empty:
            st.error("❌ Uploaded file is empty.")
            return None

        # Validate duplicate column names, which silently break
        # downstream column selection (ColumnTransformer, feature inputs)
        if df.columns.duplicated().any():
            dupes = sorted(set(df.columns[df.columns.duplicated()]))
            st.error(f"❌ Duplicate column names found: {', '.join(dupes)}. Please fix the file and re-upload.")
            return None

        # Compute metadata. dtypes/missing/duplicate-count are cached on the
        # DataFrame's content (see utils.cache.compute_dataset_metadata) so
        # a 100k+ row dataset doesn't get re-scanned on every page rerun —
        # only the first time this exact data is seen.
        num_rows, num_cols = df.shape
        column_names = list(df.columns)
        meta = compute_dataset_metadata(df)
        dtypes = meta["dtypes"]
        missing_summary = meta["missing_summary"]
        duplicate_count = meta["duplicate_count"]
        detected_targets = detect_target_candidates(df)

        return {
            "df": df,
            "filename": file_name,
            "file_size": file_size,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "column_names": column_names,
            "dtypes": dtypes,
            "missing_summary": missing_summary,
            "duplicate_count": duplicate_count,
            "detected_targets": detected_targets,
        }

    except pd.errors.EmptyDataError:
        st.error("❌ The file is empty or corrupted.")
    except pd.errors.ParserError:
        st.error("❌ The file is not a valid CSV.")
    except Exception as e:
        st.error(f"❌ An error occurred while loading the file: {str(e)}")

    return None