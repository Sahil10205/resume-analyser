# 🚀 AI Resume Analyzer — Intelligent ATS Optimization Platform

## 📌 Overview

AI Resume Analyzer is a full-stack, AI-powered web application designed to simulate real-world Applicant Tracking Systems (ATS). It leverages Natural Language Processing (NLP) and machine learning techniques to evaluate resumes against job descriptions, providing actionable insights to improve candidate shortlisting probability.

---

## 🔗 Live Deployment

* 🌐 Frontend (Vercel): https://your-vercel-link
* ⚙️ Backend API (Railway): https://your-railway-link

---

## ✨ Core Features

* 📄 **Automated Resume Parsing** using PDF text extraction
* 🎯 **ATS Score Generation** using TF-IDF vectorization and cosine similarity
* 🧠 **AI-Augmented Feedback System** with graceful fallback handling
* 🔍 **Dynamic Keyword Extraction & Matching Engine**
* 📊 **Interactive Data Visualization** using Chart.js
* ⚡ **Low-latency API Communication** with optimized request handling
* 🕓 **Client-side State Persistence** (localStorage-based history tracking)
* 🎨 **Modern UI/UX** with responsive and minimal design principles

---

## 🧠 System Architecture

```id="arch1"
Frontend (Vercel) → REST API (Flask Backend) → NLP Processing Layer → Scoring Engine → JSON Response
```

---

## 🛠️ Tech Stack

### 🔹 Frontend

* HTML5, CSS3, JavaScript (ES6+)
* Chart.js (Data Visualization)
* Fetch API (Asynchronous API communication)

### 🔹 Backend

* Python (Flask Microframework)
* Scikit-learn (TF-IDF Vectorization, Cosine Similarity)
* PyMuPDF (High-performance PDF parsing)

### 🔹 AI Integration

* Google Gemini API (LLM-based semantic analysis & feedback)

### 🔹 Deployment & DevOps

* Vercel (Frontend Hosting)
* Railway (Backend Deployment)
* Git & GitHub (Version Control)

---

## ⚙️ Functional Workflow

1. User uploads a resume and provides a job description
2. Backend performs **text extraction and normalization**
3. NLP pipeline executes:

   * Tokenization and cleaning
   * TF-IDF feature extraction
   * Cosine similarity computation
4. Keyword matching engine identifies relevant and missing terms
5. Optional AI layer generates semantic insights and improvements
6. Composite ATS score is calculated using weighted metrics
7. Results are returned and visualized on the frontend

---

## 📊 Output Metrics

* 📈 ATS Compatibility Score (0–100)
* 🧩 Keyword Match Analysis (Matched vs Missing)
* 📉 Section-wise Score Breakdown
* 🧠 AI-driven Resume Improvement Suggestions

---

## ▶️ Local Development Setup

### 1. Clone Repository

```id="clone1"
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer
```

### 2. Install Dependencies

```id="dep1"
pip install flask flask-cors scikit-learn numpy PyMuPDF
```

### 3. Run Backend Server

```id="run1"
cd backend
python app.py
```

### 4. Launch Frontend

Open `frontend/index.html` in your browser

---

## ⚠️ Operational Note

The backend is hosted on a free-tier cloud environment (Railway). Initial requests may experience slight latency due to cold-start behavior.

---

## 🚀 Future Scope & Enhancements

* Advanced semantic scoring using transformer-based models (BERT/GPT)
* Resume rewriting and optimization using generative AI
* Authentication system with personalized dashboards
* Exportable, recruiter-ready PDF reports
* Integration with job portals and ATS pipelines

---

## 👨‍💻 Author

**Sahil Sharma**
Aspiring Software Engineer | Full-Stack Developer | AI Enthusiast
