import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import logging

from utils.session_manager import is_model_trained, get_trained_model, is_dataset_uploaded, get_dataset
from utils.helpers import validate_batch_prediction_data, coerce_batch_dtypes
from utils.cache import parse_tabular_bytes
from utils.ui import (
    inject_global_css, hero, section_title, empty_state, footer, divider,
    premium_table, plotly_theme_layout, prediction_failed_alert,
)

logger = logging.getLogger(__name__)

inject_global_css()

hero(
    title="Prediction",
    subtitle="Score a single student instantly, or run batch predictions across an "
             "entire dataset — complete with confidence scores and downloadable results.",
    badge="🔮 Step 4 of 5",
    icon="🔮",
)

# Check if a model is trained (single source of truth: utils.session_manager)
if not is_model_trained():
    empty_state(
        "🤖",
        "No trained model found",
        "Please train a model first before making predictions.",
    )
    if st.button("← Back to Train Model", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Train_Model.py")
    st.stop()

model_info = get_trained_model()
model = model_info["pipeline"]
feature_columns = model_info["feature_columns"]  # always derived from training, never raw dataset columns
problem_type = model_info["problem_type"]
target_column = model_info["target_column"]
training_result = model_info["result"]

# Reference data used to infer feature dtypes for building input widgets
# and validating batch uploads. Prefer the live active dataset if it's
# still the same one the model was trained on (so filters/edits applied
# after training are reflected); otherwise fall back to the training
# snapshot the model itself carries.
active_dataset = get_dataset() if is_dataset_uploaded() else None
if active_dataset and active_dataset["filename"] == model_info["dataset_filename"]:
    reference_df = active_dataset["df"]
else:
    reference_df = training_result["X_test"] if "X_test" in training_result else None
    if reference_df is None:
        reference_df = pd.DataFrame(columns=feature_columns)

filename = model_info["dataset_filename"]

# Display model info
section_title("Model Information", icon="📊")
with st.container(border=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Model", model.named_steps['model'].__class__.__name__ if hasattr(model, 'named_steps') else model.__class__.__name__)
    col2.metric("Problem Type", problem_type.title())
    col3.metric("Target", target_column)
    col4.metric("Features", len(feature_columns))
    col5.metric("Dataset", filename)

tab1, tab2 = st.tabs(["👤 Single Student Prediction", "📁 Batch Prediction"])


def get_feature_types(df, feature_cols):
    feature_types = {}
    for col in feature_cols:
        if col not in df.columns:
            feature_types[col] = 'unknown'
            continue
        if pd.api.types.is_bool_dtype(df[col]):
            feature_types[col] = 'categorical'
        elif pd.api.types.is_integer_dtype(df[col]):
            feature_types[col] = 'integer'
        elif pd.api.types.is_float_dtype(df[col]):
            feature_types[col] = 'numeric'
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
            feature_types[col] = 'categorical'
        else:
            feature_types[col] = 'unknown'
    return feature_types


def create_single_inputs():
    """Build one input widget per trained feature column — always from
    `feature_columns` (the model's training columns), never from raw
    dataset columns, so the target column and any dropped columns can
    never appear here."""
    feature_types = get_feature_types(reference_df, feature_columns)
    inputs = {}

    st.markdown("#### Enter Student Data")
    for col in feature_columns:
        dtype = feature_types[col]

        if dtype in ('numeric', 'integer') and col in reference_df.columns and not reference_df[col].dropna().empty:
            data_min = float(reference_df[col].min())
            data_max = float(reference_df[col].max())
            data_mean = float(reference_df[col].mean())
            # Allow a modest margin beyond the observed range so users can
            # explore reasonable "what-if" values, while still guarding
            # against wildly out-of-distribution inputs.
            margin = max((data_max - data_min) * 0.2, 1.0)
            lo, hi = data_min - margin, data_max + margin

            if dtype == 'integer':
                inputs[col] = st.number_input(
                    f"{col}", min_value=int(lo), max_value=int(hi),
                    value=int(round(data_mean)), step=1,
                )
            else:
                inputs[col] = st.number_input(
                    f"{col}", min_value=lo, max_value=hi,
                    value=data_mean, step=0.1,
                )

        elif dtype == 'categorical' and col in reference_df.columns:
            unique_vals = reference_df[col].dropna().unique()
            if len(unique_vals) > 0:
                inputs[col] = st.selectbox(f"{col}", sorted(unique_vals, key=str))
            else:
                inputs[col] = st.text_input(f"{col}", "")

        else:
            inputs[col] = st.text_input(f"{col}", "")

    return inputs


def predict_single():
    with st.container(border=True):
        inputs = create_single_inputs()
        clicked = st.button("Predict", type="primary", use_container_width=True)

    if clicked:
        with st.spinner("Predicting..."):
            try:
                input_df = pd.DataFrame([inputs])[feature_columns]
                prediction = model.predict(input_df)[0]

                result = {'prediction': prediction}

                if hasattr(model, 'predict_proba'):
                    probas = model.predict_proba(input_df)[0]
                    max_proba = float(np.max(probas))
                    predicted_class = model.classes_[np.argmax(probas)]
                    result['confidence'] = max_proba
                    result['predicted_class'] = predicted_class

                return result
            except Exception:
                logger.exception("Single-record prediction failed for features=%r", feature_columns)
                prediction_failed_alert("Prediction")
                return None
    return None


def predict_batch(pred_df):
    with st.spinner("Running batch predictions..."):
        try:
            result_df = pred_df.copy()
            input_df = coerce_batch_dtypes(pred_df, feature_columns, reference_df)[feature_columns]

            predictions = model.predict(input_df)
            result_df['Prediction'] = predictions

            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba(input_df)
                max_probas = np.max(probas, axis=1)
                predicted_classes = model.classes_[np.argmax(probas, axis=1)]
                result_df['Confidence'] = max_probas
                result_df['Predicted Class'] = predicted_classes

            return result_df
        except Exception:
            logger.exception("Batch prediction failed for %d input rows", len(pred_df))
            prediction_failed_alert("Batch Prediction")
            return None


def display_results(result_df):
    if result_df is None:
        return

    st.success(f"✅ Batch prediction completed for {len(result_df)} records!")

    section_title("Prediction Results", icon="📊")
    premium_table(result_df, key="batch_prediction_results", show_download=False)

    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Prediction Results (CSV)",
        data=csv,
        file_name="prediction_results.csv",
        mime="text/csv",
        use_container_width=True
    )

    section_title("Prediction Distribution", icon="📈")

    if problem_type == "classification":
        prediction_counts = result_df["Prediction"].value_counts().reset_index()
        prediction_counts.columns = ["Prediction", "Count"]

        fig = px.bar(
            prediction_counts,
            x="Prediction",
            y="Count",
            text="Count",
            title="Distribution of Predicted Classes",
            color="Count",
            color_continuous_scale="Blues",
        )

        fig.update_layout(
            xaxis_title="Predicted Class",
            yaxis_title="Count",
            **plotly_theme_layout(),
        )

        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)

    else:  # regression
        fig = px.histogram(
            result_df,
            x="Prediction",
            nbins=20,
            title="Distribution of Predicted Values",
            color_discrete_sequence=["#2563EB"],
        )

        fig.update_layout(
            xaxis_title="Predicted Value",
            yaxis_title="Frequency",
            **plotly_theme_layout(),
        )

        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)


with tab1:
    result = predict_single()

    if result:
        st.success("✅ Prediction completed!")

        if problem_type == 'classification':
            st.metric(
                "Predicted Class",
                f"{result['predicted_class']} ({result['confidence']:.1%})"
            )
        else:
            st.metric("Predicted Value", f"{result['prediction']:.3f}")

with tab2:
    st.markdown("#### Upload Prediction Dataset")
    st.caption(f"File must contain these {len(feature_columns)} columns: {', '.join(feature_columns)}")

    pred_file = st.file_uploader(
        "Upload prediction dataset (CSV or Excel)",
        type=["csv", "xlsx"],
        key="pred_file"
    )

    if pred_file:
        try:
            file_ext = "csv" if pred_file.name.lower().endswith(".csv") else "xlsx"
            # Same cached parser used by Upload Dataset (utils.cache), so
            # re-running this page (e.g. after any other widget change)
            # doesn't re-parse the same file bytes from scratch.
            pred_df = parse_tabular_bytes(pred_file.getvalue(), file_ext)

            validation = validate_batch_prediction_data(pred_df, feature_columns, reference_df)

            if validation['errors']:
                for error in validation['errors']:
                    st.error(f"❌ {error}")
            else:
                if validation['warnings']:
                    for warning in validation['warnings']:
                        st.warning(f"⚠️ {warning}")

                result_df = predict_batch(pred_df)
                display_results(result_df)

        except Exception:
            logger.exception("Failed to read uploaded prediction file: %r", pred_file.name)
            prediction_failed_alert("File Upload")

divider()

if st.button("← Back to Train Model", use_container_width=True):
    st.switch_page("pages/4_Train_Model.py")

footer()
