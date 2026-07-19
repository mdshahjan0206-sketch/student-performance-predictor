import streamlit as st
import pandas as pd
import numpy as np
import logging
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    confusion_matrix,
    mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, roc_auc_score
)
from sklearn.impute import SimpleImputer
import time
from .config import MODEL_OPTIONS
from .helpers import validate_schema, get_numeric_columns, get_categorical_like_columns

# Server-side logger for training failures. Real exception details (with
# traceback) go here for developers; end users only ever see the clean,
# templated messages built by validate_before_training() / the
# ModelTrainingError raised from train_model() below — see TASK 1 in the
# project brief: "Never display raw Python errors to the user."
logger = logging.getLogger(__name__)


class ModelTrainingError(Exception):
    """Raised when training fails for a reason that couldn't be caught by
    pre-flight validation (validate_before_training). Callers should catch
    this specifically — never a bare `except Exception` around user-facing
    code — and show a clean message instead of this exception's raw text,
    which is logged (not displayed) for debugging."""
    pass


def detect_problem_type(df, target_column):
    """Auto-detect if target is classification or regression."""
    if len(df) == 0:
        return "classification"
    y = df[target_column]
    # ROBUSTNESS FIX: the previous check (`y.dtype in ['object','category','bool']`)
    # silently stopped matching text columns on newer pandas versions that
    # default to a dedicated string dtype (dtype name "str") instead of
    # "object" — meaning a text target like pass_fail could be
    # misdetected as regression. pd.api.types.is_numeric_dtype /
    # is_bool_dtype are the version-stable way to ask this question and
    # behave identically across pandas 1.x/2.x/3.x.
    if pd.api.types.is_bool_dtype(y) or not pd.api.types.is_numeric_dtype(y):
        return 'classification'
    # Low-cardinality numeric columns (e.g. pass/fail encoded as 0/1,
    # a 1-5 rating) behave like classes, not a continuous quantity.
    nunique = y.nunique(dropna=True)
    if nunique <= 20 or (nunique / len(df)) < 0.05:
        return 'classification'
    return 'regression'


def recommend_model(df, target_column, problem_type):
    """Recommend the best-suited model for this dataset + problem type.

    Heuristic: on small datasets, simpler linear models (Logistic/Linear
    Regression) generalize better and are less prone to overfitting than
    tree ensembles; once there's enough data (>=200 rows) a Random Forest
    is recommended since it typically handles the mixed numeric/categorical
    features and non-linear relationships in student-performance data best.
    """
    n_rows = len(df)
    if problem_type == 'classification':
        return "Logistic Regression" if n_rows < 200 else "Random Forest"
    return "Linear Regression" if n_rows < 200 else "Random Forest Regressor"


def validate_before_training(df, target_column, problem_type, model_choice):
    """
    Intelligent pre-flight validation (TASK 1): inspects dataset
    characteristics (classification vs. regression shape, sample count,
    class count/balance, missing values, dimensionality) BEFORE
    pipeline.fit() is ever called, so an unsuitable model/dataset
    combination never reaches scikit-learn as a raw exception.

    Returns a dict:
      {
        "ok": bool,                  # False => BLOCKING, do not train
        "reason": str | None,        # human-readable reason when not ok
        "recommended_models": list,  # suggested MODEL_OPTIONS entries
        "warnings": list[str],       # non-blocking heads-up messages
      }

    This does not change *how* any model is trained or scored — it only
    decides whether training should proceed, and if not, explains why in
    plain language instead of letting sklearn raise a ValueError/TypeError
    the user would otherwise see as a traceback.
    """
    warnings = []

    # --- Basic schema check (target exists / isn't 100% null) ---
    schema_ok, schema_msg = validate_schema(df, target_column)
    if not schema_ok:
        return {"ok": False, "reason": schema_msg, "recommended_models": [], "warnings": []}

    n_rows = len(df)
    if n_rows < 2:
        return {
            "ok": False,
            "reason": f"The dataset only has {n_rows} row(s). At least 2 rows are required to train any model.",
            "recommended_models": [],
            "warnings": [],
        }

    y = df[target_column]
    # Same robust check as detect_problem_type — see the comment there.
    target_is_text = pd.api.types.is_bool_dtype(y) or not pd.api.types.is_numeric_dtype(y)
    nunique = y.nunique(dropna=True)

    # --- Core compatibility check: does the chosen problem type actually
    #     fit this target column's data? ---
    if problem_type == "regression" and target_is_text:
        return {
            "ok": False,
            "reason": (
                f"'{model_choice}' cannot be used for a classification dataset. "
                f"Target column '{target_column}' contains text/category labels, not "
                f"continuous numbers, so a regression model has nothing numeric to predict."
            ),
            "recommended_models": MODEL_OPTIONS.get("classification", []),
            "warnings": [],
        }

    if problem_type == "regression" and not target_is_text and nunique < 2:
        return {
            "ok": False,
            "reason": f"Target column '{target_column}' has a single repeated value — there is nothing for a regression model to learn from.",
            "recommended_models": [],
            "warnings": [],
        }

    if problem_type == "classification" and nunique < 2:
        return {
            "ok": False,
            "reason": f"Target column '{target_column}' has only {nunique} distinct class. Classification needs at least 2.",
            "recommended_models": [],
            "warnings": [],
        }

    if problem_type == "classification" and not target_is_text and nunique > 20 and (nunique / n_rows) > 0.5:
        # Not blocking — it will still technically fit — but this is
        # almost always a mistake (a continuous column being classified).
        warnings.append(
            f"Target column '{target_column}' looks continuous ({nunique} distinct values across "
            f"{n_rows} rows). Classification will treat every unique value as its own class — "
            f"consider Regression instead for a more meaningful model."
        )

    # --- Non-blocking dataset-quality heads-up ---
    feature_count = df.shape[1] - 1
    if feature_count > n_rows:
        warnings.append(
            f"This dataset is high-dimensional relative to its size ({feature_count} feature columns vs. "
            f"{n_rows} rows). Models may overfit — consider collecting more rows or reducing columns."
        )

    if problem_type == "classification":
        class_counts = y.value_counts(dropna=True)
        if len(class_counts) > 0 and (class_counts.min() / class_counts.max()) < 0.1:
            warnings.append(
                "Class imbalance detected — some classes are much rarer than others. "
                "Accuracy alone may be misleading; check precision/recall/F1 per class."
            )

    if n_rows < 30:
        warnings.append(
            f"Only {n_rows} rows available. With so little data, evaluation metrics may be unstable "
            f"— treat results as indicative rather than definitive."
        )

    if int(df.isnull().to_numpy().any()):
        warnings.append("Missing values were detected and will be automatically imputed before training.")

    return {"ok": True, "reason": None, "recommended_models": [], "warnings": warnings}


def create_preprocessor(numeric_cols, categorical_cols):
    """Create sklearn preprocessing pipeline for numeric and categorical features."""
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )

    return preprocessor


def _build_model(problem_type, model_choice):
    """Look up and instantiate the sklearn estimator for a given problem
    type + model choice, validated against the canonical MODEL_OPTIONS
    registry in utils.config so this can never silently diverge from
    what the Train Model page's dropdown actually offers."""
    valid_choices = MODEL_OPTIONS.get(problem_type, [])
    if model_choice not in valid_choices:
        raise ValueError(
            f"'{model_choice}' is not a supported {problem_type} model. "
            f"Choose one of: {', '.join(valid_choices)}"
        )

    if problem_type == 'classification':
        if model_choice == "Logistic Regression":
            return LogisticRegression(max_iter=1000, random_state=42)
        if model_choice == "Decision Tree":
            return DecisionTreeClassifier(random_state=42)
        if model_choice == "Random Forest":
            return RandomForestClassifier(random_state=42)

    else:  # regression
        if model_choice == "Linear Regression":
            return LinearRegression()
        if model_choice == "Decision Tree Regressor":
            return DecisionTreeRegressor(random_state=42)
        if model_choice == "Random Forest Regressor":
            return RandomForestRegressor(random_state=42)

    raise ValueError(f"Unsupported model: {model_choice}")


def train_model(df, target_column, model_choice, problem_type=None):
    """Train model with preprocessing and return results.

    Returns a dict whose keys differ by problem type: classification
    results include 'confusion_matrix' and never 'residuals'; regression
    results include 'residuals' and never 'confusion_matrix'. Callers
    must branch on 'problem_type' before reading either key.
    """

    if problem_type is None:
        problem_type = detect_problem_type(df, target_column)

    X = df.drop(columns=[target_column])
    y = df[target_column]

    numeric_cols = get_numeric_columns(X)
    categorical_cols = get_categorical_like_columns(X)

    preprocessor = create_preprocessor(numeric_cols, categorical_cols)
    model = _build_model(problem_type, model_choice)

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    # Stratify classification splits so rare classes are represented in
    # both train and test sets where possible.
    stratify = y if (problem_type == 'classification' and y.nunique() > 1 and y.value_counts().min() >= 2) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    start_time = time.time()
    try:
        with st.spinner(f"Training {model_choice} on {len(X_train)} samples..."):
            pipeline.fit(X_train, y_train)
        training_time = time.time() - start_time
        y_pred = pipeline.predict(X_test)
    except Exception as exc:
        # Anything unexpected that pre-flight validation didn't catch
        # (validate_before_training) — e.g. a genuinely malformed feature
        # column — is logged in full server-side for debugging, and
        # surfaced to the user only as a clean, generic message via
        # ModelTrainingError. The raw exception text/traceback never
        # reaches the UI.
        logger.exception(
            "Training failed for model=%r, target=%r, problem_type=%r",
            model_choice, target_column, problem_type,
        )
        raise ModelTrainingError(
            f"The selected model ('{model_choice}') could not be trained on the uploaded dataset."
        ) from exc

    def _feature_importance():
        """Feature importance for tree-based models, mapped back to
        human-readable names (numeric columns + one-hot-expanded
        categorical columns)."""
        if not hasattr(model, 'feature_importances_'):
            return None, None
        importance = model.feature_importances_
        cat_names = []
        if categorical_cols:
            cat_names = list(
                pipeline.named_steps['preprocessor']
                .named_transformers_['cat']
                .named_steps['onehot']
                .get_feature_names_out(categorical_cols)
            )
        names = numeric_cols + cat_names
        return importance, names

    base_result = {
        'pipeline': pipeline,
        'problem_type': problem_type,
        'target_column': target_column,
        'feature_columns': list(X.columns),
        'training_time': training_time,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'n_train': len(X_train),
        'n_test': len(X_test),
    }

    if problem_type == 'classification':
        feature_importance, feature_names = _feature_importance()

        # ROC curve: only well-defined for binary classification, and
        # only when the estimator can produce probability scores.
        roc_data = None
        classes = list(getattr(pipeline, 'classes_', []))
        if len(classes) == 2 and hasattr(pipeline, 'predict_proba'):
            positive_class = classes[1]
            probas = pipeline.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, probas, pos_label=positive_class)
            roc_data = {
                'fpr': fpr,
                'tpr': tpr,
                'auc': roc_auc_score(y_test == positive_class, probas),
                'positive_class': positive_class,
            }

        base_result.update({
            'metrics': {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            },
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'confusion_matrix_labels': sorted(y.unique().tolist(), key=str),
            'feature_importance': feature_importance,
            'feature_names': feature_names,
            'roc_curve': roc_data,
        })
        return base_result

    # regression
    mse = mean_squared_error(y_test, y_pred)
    feature_importance, feature_names = _feature_importance()
    base_result.update({
        'metrics': {
            'mae': float(np.mean(np.abs(y_test - y_pred))),
            'mse': mse,
            'rmse': float(np.sqrt(mse)),
            'r2': r2_score(y_test, y_pred),
        },
        'residuals': y_test - y_pred,
        'feature_importance': feature_importance,
        'feature_names': feature_names,
    })
    return base_result
