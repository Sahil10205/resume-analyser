# AI Resume Analyzer

## 📌 Description
AI-based web application that analyzes resumes against job descriptions and provides ATS score and keyword suggestions.

## 🚀 Features
- Upload resume (PDF)
- ATS score using TF-IDF and cosine similarity
- Missing keyword suggestions
- Simple and clean UI

## 🛠️ Tech Stack
- Python (Flask)
- Scikit-learn (TF-IDF)
- HTML, CSS, JavaScript

## ▶️ How to Run

### 1. Install dependencies
pip install flask flask-cors scikit-learn pandas numpy spacy PyPDF2
python -m spacy download en_core_web_sm

### 2. Run backend
cd backend
python app.py

### 3. Run frontend
Open frontend/index.html in browser

## 📊 Output
- ATS Score
- Missing Keywords

## 📌 Future Improvements
- Better UI design
- More accurate NLP model
- Deployment (live hosting)