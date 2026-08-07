import streamlit as st
import pandas as pd
from utils.data_loader import load_dataset
from utils.session_manager import set_dataset, get_dataset, is_dataset_uploaded
from utils.ui import inject_global_css, hero, section_title, empty_state, footer, divider, premium_table

inject_global_css()

hero(
    title="Upload Dataset",
    subtitle="Bring in a CSV or Excel file of student records. We'll validate it and "
             "summarize everything instantly — no data ever leaves this session.",
    badge="📂 Step 1 of 5",
    icon="📂",
)

st.markdown(
    '<p style="color:#6B7280; margin-top:-0.6rem; margin-bottom:1.2rem;">'
    'Supports <strong>.csv</strong> and <strong>.xlsx</strong> formats. No data is saved or uploaded externally.'
    '</p>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx"],
    help="Supports .csv and .xlsx formats. No data is saved or uploaded externally."
)

if uploaded_file:
    result = load_dataset(uploaded_file)

    if result:
        # Store dataset in session state using shared manager. This also
        # invalidates any previously trained model, since it was fit on
        # different data (see utils/session_manager.py).
        set_dataset(
            df=result["df"],
            filename=uploaded_file.name,
            metadata={
                "file_size": result["file_size"],
                "num_rows": result["num_rows"],
                "num_cols": result["num_cols"],
                "column_names": result["column_names"],
                "dtypes": result["dtypes"],
                "missing_summary": result["missing_summary"],
                "duplicate_count": result["duplicate_count"],
                "detected_targets": result["detected_targets"],
            },
        )

        st.success(f"✅ **{uploaded_file.name}** uploaded successfully!")

        # Display metadata in cards
        section_title("Dataset Summary", icon="🗂️")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("File Name", uploaded_file.name)
        col2.metric("File Size", f"{result['file_size'] / 1024:.1f} KB")
        col3.metric("Rows", result["num_rows"])
        col4.metric("Columns", result["num_cols"])

        # Target-column validation: does this look like a student
        # performance dataset at all? Surfaced here (rather than only at
        # training time) so the user knows immediately if they'll need
        # to pick a target column manually later.
        section_title("Target Column Check", icon="🎯")
        if result["detected_targets"]:
            st.success(
                f"✅ Detected likely target column(s): **{', '.join(result['detected_targets'])}**. "
                "You'll be able to confirm or change this on the Train Model page."
            )
        else:
            st.warning(
                "⚠️ No standard student-performance column (e.g. exam_score, grade, pass_fail, "
                "performance) was detected by name. You'll need to select a target column "
                "manually on the Train Model page."
            )

        # Display column information, missing values, duplicates, and preview
        section_title("Column Information", icon="📊")
        with st.container(border=True):
            # Chunk into rows so wide datasets (many columns) don't
            # squeeze st.columns() into unreadably narrow slivers.
            chunk_size = 6
            col_names = result['column_names']
            for start in range(0, len(col_names), chunk_size):
                chunk = col_names[start:start + chunk_size]
                row_cols = st.columns(len(chunk))
                for c, col_name in zip(row_cols, chunk):
                    c.write(f"**{col_name}**\n{result['dtypes'][col_name]}")

        section_title("Missing Values", icon="⚠️")
        missing_df = pd.DataFrame.from_dict(result['missing_summary'], orient='index', columns=['Missing'])
        missing_df = missing_df[missing_df['Missing'] > 0]
        if not missing_df.empty:
            total_missing = int(missing_df['Missing'].sum())
            st.warning(f"⚠️ {total_missing:,} missing value(s) found across {len(missing_df)} column(s). "
                       "These will be automatically imputed during training.")
            premium_table(missing_df, key="missing_values", index_label="Column", download_filename="missing_values.csv")
        else:
            st.success("✅ No missing values found.")

        section_title("Duplicates", icon="🧬")
        if result['duplicate_count'] > 0:
            st.warning(f"⚠️ {result['duplicate_count']:,} duplicate row(s) detected. "
                       "They won't be removed automatically — review them on the Data Analysis page if needed.")
        st.metric("Duplicate Rows", result['duplicate_count'])

        section_title("Preview", icon="🔎", subtitle="First 10 rows")
        premium_table(result['df'].head(10), key="dataset_preview", show_download=False)

        divider()

        # Navigation button to next page
        if st.button("📊 Analyze Dataset", type="primary", use_container_width=True):
            st.switch_page("pages/3_Data_Analysis.py")

else:
    if is_dataset_uploaded():
        dataset = get_dataset()
        st.success(f"✅ Dataset '{dataset['filename']}' is ready for analysis.")
    else:
        empty_state(
            "📥",
            "No dataset uploaded yet",
            "Drag & drop a CSV or Excel file above, or click to browse your files.",
        )

footer()
