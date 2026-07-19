import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap
import logging

from utils.session_manager import (
    get_dataset,
    is_dataset_uploaded,
    set_trained_model,
    get_trained_model,
    is_model_trained,
)

from utils.model_trainer import (
    train_model,
    detect_problem_type,
    recommend_model,
    validate_before_training,
    ModelTrainingError,
)
from utils.helpers import detect_target_candidates
from utils.config import MODEL_OPTIONS

from utils.ui import (
    inject_global_css, hero, section_title, empty_state, footer, divider,
    custom_radio, plotly_theme_layout, model_incompatibility_alert, training_failed_alert,
)

logger = logging.getLogger(__name__)

inject_global_css()

hero(
    title="Train Model",
    subtitle="Build and evaluate machine learning models with our intelligent "
             "training pipeline — preprocessing, splitting, and scoring handled automatically.",
    badge="🤖 Step 3 of 5",
    icon="🤖",
)


def render_results(result):
    """Render the full training results view (metrics, confusion matrix /
    residual plot, feature importance) from a stored result dict. Kept as
    a standalone function — rather than living only inside the "Train"
    button's if-block — so the results stay visible across reruns (e.g.
    navigating to another page and back) instead of disappearing as soon
    as any other widget triggers a rerun.
    """
    problem_type = result['problem_type']
    metrics = result['metrics']

    section_title("Training Summary", icon="📊")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Training Samples", result['n_train'])
        with col2:
            st.metric("Testing Samples", result['n_test'])

    section_title("Model Performance", icon="📈")
    with st.container(border=True):
        cols = st.columns(4)
        if problem_type == 'classification':
            cols[0].metric("Accuracy", f"{metrics['accuracy']:.3f}")
            cols[1].metric("Precision", f"{metrics['precision']:.3f}")
            cols[2].metric("Recall", f"{metrics['recall']:.3f}")
            cols[3].metric("F1-Score", f"{metrics['f1']:.3f}")
        else:
            cols[0].metric("MAE", f"{metrics['mae']:.3f}")
            cols[1].metric("MSE", f"{metrics['mse']:.3f}")
            cols[2].metric("RMSE", f"{metrics['rmse']:.3f}")
            cols[3].metric("R²", f"{metrics['r2']:.3f}")

    # Classification-only: Confusion Matrix. Never shown for regression.
    if problem_type == 'classification':
        section_title("Confusion Matrix", icon="🧩")
        cm = result['confusion_matrix']
        labels = result.get('confusion_matrix_labels')
        fig = px.imshow(
            cm,
            text_auto=True,
            x=labels, y=labels,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            title="Confusion Matrix",
            color_continuous_scale="Blues",
        )
        fig.update_layout(**plotly_theme_layout())
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)

    # Classification-only, binary only: ROC Curve. Absent for
    # multi-class targets or regression.
    if problem_type == 'classification' and result.get('roc_curve') is not None:
        roc = result['roc_curve']
        section_title("ROC Curve", icon="📐")
        fig = px.area(
            x=roc['fpr'], y=roc['tpr'],
            labels={'x': 'False Positive Rate', 'y': 'True Positive Rate'},
            title=f"ROC Curve (AUC = {roc['auc']:.3f})",
            color_discrete_sequence=["#2563EB"],
        )
        fig.add_shape(type="line", line=dict(dash="dash", color="#94A3B8"), x0=0, x1=1, y0=0, y1=1)
        fig.update_yaxes(scaleanchor="x", scaleratio=1, range=[0, 1])
        fig.update_xaxes(range=[0, 1])
        fig.update_layout(**plotly_theme_layout())
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)

    # Regression-only: Residual Plot. Never shown for classification.
    if problem_type == 'regression':
        section_title("Residual Plot", icon="📉")
        fig = px.scatter(
            x=result['y_pred'],
            y=result['residuals'],
            labels={'x': 'Predicted', 'y': 'Residuals'},
            title='Residuals vs Predicted',
            color_discrete_sequence=["#2563EB"],
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#EF4444")
        fig.update_layout(**plotly_theme_layout())
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)

    if result.get('feature_importance') is not None:
        section_title("Feature Importance", icon="🔝")
        importance_df = pd.DataFrame({
            'Feature': result['feature_names'],
            'Importance': result['feature_importance']
        }).sort_values('Importance', ascending=False).head(10)

        fig = px.bar(
            importance_df,
            x='Importance',
            y='Feature',
            orientation='h',
            title='Top 10 Feature Importances',
            color='Importance',
            color_continuous_scale='Blues',
        )
        fig.update_layout(**plotly_theme_layout())
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, theme=None)


if not is_dataset_uploaded():
    empty_state(
        "📂",
        "No dataset uploaded",
        "Please upload a dataset to begin training a model.",
    )
    if st.button("← Back to Upload", key="back_upload", type="primary"):
        st.switch_page("pages/2_Upload_Dataset.py")
else:
    dataset = get_dataset()
    df = dataset["df"]

    section_title("Dataset Loaded", icon="✅")
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Filename", dataset['filename'])
        m2.metric("Rows", len(df))
        m3.metric("Columns", len(df.columns))

    section_title(
        "Configure Training", icon="⚙️",
        subtitle="We automatically detect a student-performance target column (e.g. exam_score, "
                  "grade, pass_fail) — you can override this manually if needed."
    )

    with st.container(border=True):
        # --- Target column: auto-detect first, manual override available ---
        candidates = detect_target_candidates(df)

        if candidates:
            st.caption(f"🎯 Detected likely target column(s): {', '.join(candidates)}")
            target_column = st.selectbox(
                "Select Target Column",
                candidates,
                key="target_column_selector",
            )
            with st.expander("⚙️ Advanced: use a different column as the target"):
                use_manual = st.checkbox("Choose any column manually", key="manual_target_override")
                if use_manual:
                    target_column = st.selectbox(
                        "Target Column (manual)",
                        df.columns.tolist(),
                        key="manual_target_column_selector",
                    )
        else:
            st.warning(
                "⚠️ No standard student-performance column (e.g. exam_score, grade, "
                "pass_fail, performance) was detected automatically. Please choose the "
                "column you want to predict manually."
            )
            target_column = st.selectbox(
                "Select Target Column",
                df.columns.tolist(),
                key="manual_target_column_selector_fallback",
            )

        # Auto-detect problem type, with manual override
        auto_problem_type = detect_problem_type(df, target_column)

        problem_type_override = custom_radio(
            "Problem Type",
            ["Auto-detect", "Classification", "Regression"],
            index=0,
            key="problem_type_override",
        )

        if problem_type_override == "Classification":
            problem_type = "classification"
        elif problem_type_override == "Regression":
            problem_type = "regression"
        else:
            problem_type = auto_problem_type

        st.caption(f"Detected problem type: **{auto_problem_type.title()}**" +
                   (" (overridden below)" if problem_type != auto_problem_type else ""))

        model_options = MODEL_OPTIONS[problem_type]
        recommended_model = recommend_model(df, target_column, problem_type)
        st.caption(f"🌟 Recommended model for this dataset: **{recommended_model}**")

        model_choice = st.selectbox("Choose Model", model_options, key="model_choice")

        if model_choice != recommended_model:
            st.warning(
                f"⚠️ '{model_choice}' is not the suggested model for this dataset. "
                f"'{recommended_model}' is recommended for better performance."
            )

        st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)

        train_clicked = st.button("🚀 Train Model", type="primary", use_container_width=True)

    if train_clicked:
        validation = validate_before_training(df, target_column, problem_type, model_choice)

        if not validation["ok"]:
            model_incompatibility_alert(validation["reason"], validation["recommended_models"])
        else:
            for warning_msg in validation["warnings"]:
                st.warning(f"⚠️ {warning_msg}")

            try:
                with st.spinner("Training model..."):
                    result = train_model(df, target_column, model_choice, problem_type)
            except ModelTrainingError:
                # Real exception already logged inside train_model();
                # only the clean, professional message is shown here.
                training_failed_alert()
            except Exception:
                # Safety net for anything raised outside train_model's own
                # try/except (e.g. during result post-processing) — still
                # never leaks raw Python errors to the user.
                logger.exception(
                    "Unexpected error while training model=%r on target=%r",
                    model_choice, target_column,
                )
                training_failed_alert()
            else:
                set_trained_model(
                    pipeline=result['pipeline'],
                    feature_columns=result['feature_columns'],
                    target_column=result['target_column'],
                    problem_type=result['problem_type'],
                    result=result,
                    dataset_filename=dataset['filename'],
                )

                st.success(f"✅ Training completed in {result['training_time']:.2f} seconds!")
                render_results(result)

    # Always show results + the "go to prediction" CTA from session state so
    # they persist across reruns, not just immediately after clicking Train.
    if is_model_trained() and not train_clicked:
        model_info = get_trained_model()
        if model_info['dataset_filename'] == dataset['filename']:
            st.markdown(
                textwrap.dedent(
                    """
                    <div style="text-align: center; margin: 1rem 0 1.6rem 0;">
                        <div class="pp-badge success" style="font-size:1rem; padding:10px 22px;">
                            ✅ Model trained successfully! Showing results from your last training run.
                        </div>
                    </div>
                    """
                ).strip(),
                unsafe_allow_html=True,
            )
            render_results(model_info['result'])

    if is_model_trained():
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Go to Prediction", use_container_width=True, type="primary"):
            st.switch_page("pages/5_Prediction.py")

divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("← Back to Analysis", key="back_analysis"):
        st.switch_page("pages/3_Data_Analysis.py")

footer()
