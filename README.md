# 🎓 EduPredict AI – Student Performance Predictor

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-Web%20Application-red?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
</p>

> **EduPredict AI** is an AI-powered Student Performance Prediction System that leverages Machine Learning and Data Science to analyze educational datasets, train predictive models, and forecast student academic performance through a modern, interactive, and user-friendly web application.

---

# 📖 Overview

EduPredict AI helps educators, researchers, and students make data-driven decisions by analyzing student performance data and generating accurate predictions using multiple machine learning algorithms.

The application offers a premium dashboard, automated data preprocessing, intelligent model validation, interactive visualizations, and downloadable prediction results—all without requiring programming knowledge.

---

# ✨ Key Features

## 📂 Dataset Management
- Upload CSV datasets
- Automatic dataset validation
- Missing value detection
- Duplicate record detection
- Data type inspection
- Preview uploaded dataset
- Large dataset support (100,000+ rows)

---

## 🧹 Data Preprocessing

- Automatic missing value handling
- Label Encoding
- One-Hot Encoding
- Feature Scaling
- Feature Selection
- Data Cleaning
- Numerical & Categorical feature processing
- Target column identification

---

## 🤖 Machine Learning Models

Supports multiple machine learning algorithms including:

- Random Forest
- Decision Tree
- Logistic Regression
- Support Vector Machine (SVM)
- K-Nearest Neighbors (KNN)
- Naive Bayes
- XGBoost *(if installed)*

---

## 🧠 Intelligent Model Validation

Before training, EduPredict AI automatically checks whether the selected algorithm is compatible with the uploaded dataset.

Instead of displaying technical Python or Scikit-learn errors, the system provides:

- Professional validation messages
- Model compatibility checks
- Recommended alternative algorithms
- Graceful error handling

Example:

```
⚠ Selected Model Not Recommended

The selected model is not suitable for your dataset.

Recommended Models:
✔ Random Forest Classifier
✔ Decision Tree Classifier
✔ Logistic Regression
```

---

## 📊 Model Training

- One-click model training
- Automatic train-test split
- Efficient model fitting
- Cached training pipeline
- Fast execution

---

## 📈 Model Evaluation

Automatically calculates:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- Classification Report

---

## 🔮 Student Performance Prediction

Predict academic performance using trained models.

The system supports:

- Batch Prediction
- Dataset Prediction
- Single Prediction
- Result Visualization

---

## 📊 Interactive Dashboard

Modern dashboard with:

- Dataset statistics
- Performance metrics
- Interactive charts
- Feature distributions
- Model comparison
- Prediction summaries

---

## 📉 Data Visualization

Interactive visualizations powered by Plotly and Matplotlib:

- Bar Charts
- Pie Charts
- Histograms
- Correlation Heatmaps
- Confusion Matrix
- Feature Importance
- Distribution Graphs

---

## 📥 Export Results

Download:

- Prediction Results (CSV)
- Processed Dataset
- Evaluation Results

---

## ⚡ Performance Optimization

The application is optimized using Streamlit caching.

Features include:

- Cached dataset loading
- Cached preprocessing
- Cached machine learning models
- Faster page loading
- Reduced memory usage
- Lazy loading
- Optimized visualizations

---

## 🎨 Premium User Interface

- Modern responsive design
- Glassmorphism UI
- Animated buttons
- Interactive cards
- Smooth transitions
- Professional layout
- Mobile-friendly interface
- Light theme support

---

# 🔄 Prediction Workflow

```
Upload Dataset
        │
        ▼
Dataset Validation
        │
        ▼
Data Cleaning
        │
        ▼
Feature Encoding
        │
        ▼
Feature Scaling
        │
        ▼
Target Selection
        │
        ▼
Model Selection
        │
        ▼
Compatibility Check
        │
        ▼
Model Training
        │
        ▼
Model Evaluation
        │
        ▼
Student Prediction
        │
        ▼
Download Results
```

---

# 🛠 Technology Stack

## Programming Language

- Python

## Frontend

- Streamlit
- HTML5
- CSS3
- JavaScript

## Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Joblib

## Data Visualization

- Plotly
- Matplotlib

---

# 📁 Project Structure

```
student-performance-predictor/
│
├── assets/
│   ├── css/
│   └── images/
│
├── data/
│
├── models/
│
├── pages/
│
├── utils/
│
├── app.py
├── model.pkl
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

## Clone the Repository

```bash
git clone https://github.com/mdshahjan0206-sketch/student-performance-predictor.git
```

Move into the project directory

```bash
cd student-performance-predictor
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 🚀 Live Demo

**Render Deployment**

https://student-performance-predictor-8nwv.onrender.com

---

# 📸 Screenshots

Add screenshots of:

- Home Page
- Dashboard
- Dataset Upload
- Prediction Page
- Analytics Dashboard
- Results Page

---

# 🎯 Future Enhancements

- Deep Learning Models
- Explainable AI (SHAP)
- AutoML Support
- PDF Report Generation
- User Authentication
- Cloud Database Integration
- REST API
- Real-time Prediction Service
- Multi-language Support

---

# 👨‍💻 Developer

**Mohamed Shahjan**

B.E. Computer Science Engineering

### Areas of Interest

- Artificial Intelligence
- Machine Learning
- Data Science
- Python Development
- Data Analytics

**GitHub**

https://github.com/mdshahjan0206-sketch

---

# ⭐ Support

If you found this project useful, please consider giving it a **⭐ Star** on GitHub.

Your support motivates future development and helps others discover the project.

---

# 📜 License

This project is developed for **educational, research, and learning purposes**.

---

# ❤️ Acknowledgements

Special thanks to the open-source community and the developers of **Streamlit**, **Scikit-learn**, **Pandas**, **NumPy**, **Matplotlib**, and **Plotly** for providing the powerful tools that made this project possible.
