"""Single source of truth for all cross-page session state.

Two things are tracked here, each under its own top-level key so pages
never need to poke at st.session_state directly (and can't accidentally
create a second, inconsistent copy of the same data):

  st.session_state["dataset"] -> the uploaded/active DataFrame + metadata
  st.session_state["model"]   -> the trained pipeline + training metadata

Whenever a *new* dataset is uploaded, any previously trained model is
invalidated (cleared), since a model trained on the old data is no
longer valid for the new one. This is the fix for the bug where
uploading a second file left the Prediction page silently using a
stale model trained on the first file.
"""

import streamlit as st


# ----------------------------- Dataset ----------------------------------

def set_dataset(df, filename=None, metadata=None):
    """Register the active dataset. Always invalidates any previously
    trained model, since it was trained against different data."""
    if filename is None:
        raise TypeError("filename is required")

    st.session_state["dataset"] = {
        "df": df,
        "filename": filename,
        "metadata": metadata,
        "uploaded": True,
    }
    clear_trained_model()

    # A newly uploaded file may not have the same columns as the previous
    # one, so any widget selection tied to the old column set (target
    # column, model choice, etc.) must be dropped rather than left stale
    # in session_state, where it could otherwise raise a Streamlit
    # "value not in options" error the next time Train Model renders.
    for widget_key in (
        "target_column_selector",
        "manual_target_column_selector",
        "manual_target_column_selector_fallback",
        "manual_target_override",
        "model_choice",
        "problem_type_override",
    ):
        st.session_state.pop(widget_key, None)


def get_dataset():
    return st.session_state.get("dataset", None)


def is_dataset_uploaded():
    dataset = st.session_state.get("dataset")
    return bool(dataset and dataset.get("uploaded") and dataset.get("df") is not None)


def clear_dataset():
    """Clear dataset (and any dependent trained model) from session state."""
    st.session_state["dataset"] = {
        "df": None,
        "filename": None,
        "metadata": None,
        "uploaded": False,
    }
    clear_trained_model()


# --------------------------- Trained model -------------------------------

def set_trained_model(pipeline, feature_columns, target_column, problem_type, result, dataset_filename):
    """Register the most recently trained model. `result` is the full
    metrics/plots dict returned by utils.model_trainer.train_model(),
    kept so the results view can be re-rendered after a rerun without
    retraining."""
    st.session_state["model"] = {
        "pipeline": pipeline,
        "feature_columns": feature_columns,
        "target_column": target_column,
        "problem_type": problem_type,
        "result": result,
        "dataset_filename": dataset_filename,
    }
    st.session_state["training_complete"] = True


def get_trained_model():
    return st.session_state.get("model", None)


def is_model_trained():
    return bool(st.session_state.get("training_complete") and st.session_state.get("model"))


def clear_trained_model():
    st.session_state["model"] = None
    st.session_state["training_complete"] = False
