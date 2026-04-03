# 🚀 AI Resume Analyzer — Intelligent ATS Optimization Platform

## 📌 Overview

AI Resume Analyzer is a full-stack, AI-powered web application designed to simulate real-world Applicant Tracking Systems (ATS). It leverages Natural Language Processing (NLP) techniques to evaluate resumes against job descriptions and generate actionable insights to improve candidate shortlisting probability.

---

## 🔗 Live Deployment

* 🌐 **Live Application:** https://resume-analyser-ep79ya043-sahil10205.vercel.app/
* ⚙️ **Backend API:** https://resume-analyser-production-93d7.up.railway.app
* 💻 **GitHub Repository:** https://github.com/Sahil10205/resume-analyser

---

## ✨ Key Features

* 📄 Automated PDF resume parsing
* 🎯 ATS score generation using TF-IDF and cosine similarity
* 🔍 Keyword matching and missing keyword detection
* 📊 Interactive data visualization using Chart.js
* ⚡ Speedtest-style circular ATS score animation for enhanced UX
* 🕓 Local history tracking using browser storage
* 🧠 AI-based feedback system with fallback handling (graceful degradation)
* 🛡️ Robust error handling for API failures and edge cases

---

## 🧠 System Architecture

```
Frontend (Vercel) → Flask Backend (Railway) → NLP Processing → Scoring Engine → JSON Response
```

---

## 🛠️ Tech Stack

### 🔹 Frontend

* HTML5, CSS3, JavaScript
* Chart.js (Data Visualization)
* Fetch API (Asynchronous API communication)

### 🔹 Backend

* Python (Flask)
* Scikit-learn (TF-IDF Vectorization, Cosine Similarity)
* PyMuPDF (PDF parsing)

### 🔹 Deployment

* Vercel (Frontend Hosting)
* Railway (Backend Deployment)
* Git & GitHub (Version Control)

---

## ⚙️ Functional Workflow

1. User uploads a resume (PDF) and provides a job description
2. Backend performs text extraction and normalization
3. NLP pipeline executes TF-IDF feature extraction and similarity computation
4. Keyword matching engine identifies relevant and missing terms
5. Optional AI layer generates semantic insights (with fallback handling)
6. Composite ATS score is calculated using weighted metrics
7. Results are returned and visualized on the frontend

---

## 📊 Output

* 📈 ATS Score (Speedtest-style circular visualization)
* 📉 Score breakdown (TF-IDF, Keywords, Sections)
* 🕓 Analysis history tracking

---

## ▶️ Local Setup

### 1. Clone Repository

```
git clone https://github.com/Sahil10205/resume-analyser.git
cd resume-analyser
```

### 2. Install Dependencies

```
pip install flask flask-cors scikit-learn numpy PyMuPDF
```

### 3. Run Backend

```
cd backend
python app.py
```

### 4. Run Frontend

Open `frontend/index.html` in your browser

---

## ⚠️ Note

The backend is hosted on a free-tier cloud service (Railway), so the first request may take a few seconds due to cold-start latency.

---

## 🚀 Future Enhancements

* Advanced NLP models (BERT / Transformers)
* AI-powered resume rewriting suggestions
* User authentication & personalized dashboard
* Exportable recruiter-ready PDF reports
* Integration with job portals and ATS pipelines

---

## 👨‍💻 Author

**Sahil Sharma**
Aspiring Software Engineer | Full-Stack Developer | AI Enthusiast
