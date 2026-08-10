# 🎓 AI Student Performance Predictor

An AI-powered **Student Performance Prediction System** built using **Python, Streamlit, and Machine Learning**. The application allows users to upload and validate datasets, explore student data, analyze important factors, and predict student performance through an interactive web interface.

## 🚀 Project Overview

Student performance is influenced by various academic, demographic, social, and behavioral factors. This project uses machine learning and data analysis techniques to identify these patterns and provide student performance predictions.

The system provides an interactive dashboard where users can:

- 📊 Explore student datasets
- 📁 Upload and validate CSV datasets
- 🤖 Predict student performance using Machine Learning
- 📈 Analyze model performance
- 🔍 Identify important performance factors
- 📄 Generate prediction reports
- 📥 Export results as CSV
- 🌐 Use the complete system through a Streamlit web application

---

## ✨ Features

### 🏠 Home
- Project introduction
- Project statistics
- Feature overview
- Quick navigation

### 📁 Dataset Upload & Validation
- Upload CSV datasets
- Automatically detect dataset columns
- Validate required features
- Detect missing values
- Detect duplicate records
- Identify numeric and categorical columns
- Display validation results before prediction

### 📊 Dataset Overview
- Dataset preview
- Column information
- Data types
- Missing-value analysis
- Statistical summary
- Correlation analysis
- Interactive visualizations

### 🎯 Student Performance Prediction
- Enter student-related information
- Process input through the ML pipeline
- Predict student performance
- Display prediction results
- Display prediction confidence where supported
- Generate downloadable reports

### 📈 Dashboard
Interactive visualizations including:

- Study time vs performance
- Absences vs performance
- Feature importance
- Academic factors
- Student demographics
- Correlation analysis
- Performance distributions

### 🧠 Model Insights
- Model evaluation metrics
- Feature importance
- Confusion matrix
- ROC analysis where applicable
- Model methodology
- Preprocessing explanation

### 📄 Reports & Export
- Download prediction reports
- Export prediction history
- Export analysis results as CSV

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application framework |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computation |
| Scikit-learn | Machine Learning |
| Plotly | Interactive visualizations |
| Matplotlib | Data visualization |
| Joblib | Model/artifact handling |
| ReportLab | PDF report generation |
| Statsmodels | Statistical analysis |

---

## 🤖 Machine Learning

The project uses a machine learning pipeline for student performance prediction.

### Pipeline

```text
Dataset
   ↓
Data Validation
   ↓
Data Preprocessing
   ↓
Feature Encoding
   ↓
Feature Scaling
   ↓
Machine Learning Model
   ↓
Prediction
   ↓
Performance Analysis
   ↓
Visualization
