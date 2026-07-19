# 🎓 EduPredict AI – Student Performance Predictor

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-Web%20Application-red?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange?style=for-the-badge&logo=scikitlearn" alt="Scikit-Learn">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Production-success?style=for-the-badge" alt="Status">
</p>

<p align="center">
An AI-powered Student Performance Prediction System that enables educators, students, and researchers to analyze academic datasets, train machine learning models, evaluate performance, and generate accurate student performance predictions through a modern, responsive web application.
</p>

---

# 🌟 Overview

EduPredict AI is a comprehensive Machine Learning web application designed to simplify educational data analysis and student performance prediction.

The system integrates data preprocessing, multiple machine learning algorithms, intelligent model validation, interactive visualizations, performance evaluation, and downloadable prediction reports into one user-friendly platform.

Whether you're an educator, student, or researcher, EduPredict AI makes predictive analytics accessible without requiring programming expertise.

---

# 🚀 Production Deployment

The application is fully deployed and publicly accessible.

### 🌐 Web Application

**https://student-performance-predictor-8nwv.onrender.com**

---

# ✨ Features

## 📂 Dataset Management

- Upload CSV datasets
- Automatic dataset validation
- Preview uploaded datasets
- Missing value detection
- Duplicate record detection
- Data type analysis
- Large dataset support (100,000+ records)

---

## 🧹 Data Preprocessing

Automatically performs:

- Missing value handling
- Label Encoding
- One-Hot Encoding
- Feature Scaling
- Feature Selection
- Data Cleaning
- Numerical feature processing
- Categorical feature processing

---

## 🤖 Machine Learning Models

Supports multiple machine learning algorithms:

- Random Forest
- Decision Tree
- Logistic Regression
- Support Vector Machine (SVM)
- K-Nearest Neighbors (KNN)
- Naive Bayes
- XGBoost *(Optional)*

---

## 🧠 Intelligent Model Validation

The application automatically verifies whether the selected machine learning model is compatible with the uploaded dataset.

Instead of displaying technical Python or Scikit-learn exceptions, EduPredict AI provides user-friendly validation messages with recommended alternative models.

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

## ⚙ Model Training

- One-click model training
- Automatic Train-Test Split
- Efficient model fitting
- Cached training pipeline
- Optimized execution

---

## 📊 Model Evaluation

Automatically computes:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- Classification Report

---

## 🔮 Student Performance Prediction

Generate predictions using trained machine learning models.

Supports:

- Batch Prediction
- Dataset Prediction
- Individual Student Prediction
- Prediction Summary

---

## 📈 Interactive Dashboard

Interactive dashboard featuring:

- Dataset statistics
- Prediction summary
- Model comparison
- Performance metrics
- Interactive charts
- Feature distributions

---

## 📉 Data Visualization

Visualizations include:

- Bar Charts
- Pie Charts
- Histograms
- Correlation Heatmaps
- Feature Importance
- Confusion Matrix
- Distribution Graphs

---

## 📥 Export Results

Download:

- Prediction Results
- Processed Dataset
- Evaluation Metrics

---

## ⚡ Performance Optimization

Optimized using Streamlit caching:

- Cached dataset loading
- Cached preprocessing
- Cached model loading
- Faster predictions
- Reduced memory usage
- Lazy loading
- Optimized chart rendering

---

## 🎨 Premium User Interface

- Modern Design
- Glassmorphism UI
- Responsive Layout
- Animated Components
- Interactive Cards
- Smooth Navigation
- Mobile Friendly
- Professional Light Theme

---

# 🔄 Prediction Workflow

```
User Uploads Dataset
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
Machine Learning Model Selection
          │
          ▼
Model Compatibility Validation
          │
          ▼
Model Training
          │
          ▼
Performance Evaluation
          │
          ▼
Student Performance Prediction
          │
          ▼
Visualization & Analytics
          │
          ▼
Download Prediction Results
```

---

# 🛠 Technology Stack

### Programming Language

- Python

### Web Framework

- Streamlit

### Machine Learning

- Scikit-learn
- Joblib

### Data Processing

- Pandas
- NumPy

### Data Visualization

- Plotly
- Matplotlib

### Frontend

- HTML5
- CSS3
- JavaScript

---

# 📁 Project Structure

```
student-performance-predictor/
│
├── assets/
│   ├── css/
│   ├── images/
│   └── icons/
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
├── README.md
└── LICENSE
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/mdshahjan0206-sketch/student-performance-predictor.git
```

## Navigate to Project

```bash
cd student-performance-predictor
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Launch Application

```bash
streamlit run app.py
```

---

# 📸 Screenshots

Add screenshots of the following pages:

- 🏠 Home Page
- 📊 Dashboard
- 📂 Dataset Upload
- 🤖 Prediction Page
- 📈 Analytics Dashboard
- 📉 Evaluation Results

---

# 🎯 Future Enhancements

- Deep Learning Models
- Explainable AI (SHAP)
- AutoML Integration
- PDF Report Generation
- User Authentication
- Database Integration
- REST API
- Real-time Prediction Service
- Multi-language Support
- Cloud Model Deployment

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve this project:

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 👨‍💻 Developer

## Mohamed Shahjan

**B.E. Computer Science Engineering**

### Areas of Interest

- Artificial Intelligence
- Machine Learning
- Data Science
- Python Development
- Web Application Development

### GitHub

https://github.com/mdshahjan0206-sketch

---

# ⭐ Support

If you found this project useful, please consider giving it a **⭐ Star** on GitHub.

Your support helps others discover the project and motivates future improvements.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 🙏 Acknowledgements

Special thanks to the developers and contributors of:

- Streamlit
- Scikit-learn
- Pandas
- NumPy
- Plotly
- Matplotlib

for providing the open-source tools that made this project possible.

---

<p align="center">
<strong>EduPredict AI</strong><br>
Empowering Education Through Artificial Intelligence and Machine Learning.
</p>
