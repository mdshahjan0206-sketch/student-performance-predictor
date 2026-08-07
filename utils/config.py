"""Central configuration for the app: paths, model registry, and the
keyword list used to auto-detect a valid "student performance" target
column. Keeping these in one place removes the duplicated/mismatched
literals that used to be scattered across pages and utils modules.
"""

import os

# --- Paths -------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
DATA_DIR = os.path.join(ROOT_DIR, "data")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
CSS_DIR = os.path.join(ASSETS_DIR, "css")

# --- Model registry ------------------------------------------------------
# Single source of truth for model choices, keyed by problem type. Both
# the Train Model page (dropdown options) and utils.model_trainer
# (dispatch logic) import from here so the two can never drift apart.
MODEL_OPTIONS = {
    "classification": ["Logistic Regression", "Decision Tree", "Random Forest"],
    "regression": ["Linear Regression", "Decision Tree Regressor", "Random Forest Regressor"],
}

# --- Target-column auto-detection ---------------------------------------
# Ordered by priority (most specific / most common first). A column name
# is treated as a candidate target if, after stripping non-alphanumeric
# characters, it contains one of these keywords (or vice versa).
TARGET_COLUMN_KEYWORDS = [
    "exam_score", "examscore", "final_score", "test_score", "final_grade",
    "placement_status", "placed",
    "performance_index", "performance",
    "pass_fail", "passfail", "passed",
    "grade", "gpa", "cgpa",
    "result", "outcome",
    "target", "label",
]

# --- Charting --------------------------------------------------------
COLOR_PALETTE = [
    "#6366F1",  # primary (indigo)
    "#8B5CF6",  # secondary (purple)
    "#10B981",  # success
    "#F59E0B",  # warning
    "#EF4444",  # danger
    "#3B82F6",  # line (for trend)
]

CHART_TYPES = ["Histogram", "Box Plot", "Value Counts"]
