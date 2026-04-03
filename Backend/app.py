import os
import re
import json

from flask import Flask, request, jsonify
from flask_cors import CORS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import fitz  # PyMuPDF

from google import genai

# ---------------- APP SETUP ----------------
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend is running successfully"

# ---------------- GEMINI SETUP ----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = None

try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini client initialized")
    else:
        print("❌ GEMINI_API_KEY missing")
except Exception as e:
    print("❌ Gemini init error:", e)
    client = None


# ================================================================
#  1. PDF TEXT EXTRACTION
# ================================================================
def extract_text(file) -> str:
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "".join(page.get_text() for page in pdf)
    except Exception:
        return file.read().decode(errors="ignore")


# ================================================================
#  2. TEXT CLEANING
# ================================================================
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+ ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ================================================================
#  3. DYNAMIC KEYWORD EXTRACTION
# ================================================================
def dynamic_keyword_score(resume: str, job_desc: str):
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=500
        )
        vectorizer.fit([job_desc])

        feature_names = vectorizer.get_feature_names_out()
        jd_vector     = vectorizer.transform([job_desc]).toarray()[0]

        top_indices  = jd_vector.argsort()[::-1][:30]
        top_keywords = [feature_names[i] for i in top_indices if jd_vector[i] > 0]

        resume_clean = clean_text(resume)

        matched = [kw for kw in top_keywords if kw in resume_clean]
        missing = [kw for kw in top_keywords if kw not in resume_clean]

        score = (len(matched) / len(top_keywords) * 100) if top_keywords else 0
        return round(score, 2), matched[:15], missing[:15]

    except Exception:
        return 0.0, [], []


# ================================================================
#  4. TF-IDF COSINE SIMILARITY
# ================================================================
def tfidf_score(resume: str, job_desc: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf      = vectorizer.fit_transform([resume, job_desc])
        return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100)
    except Exception:
        return 0.0


# ================================================================
#  5. SECTION DETECTION
# ================================================================
def section_score(resume: str):
    sections = ["education", "skills", "projects", "experience",
                "summary", "certifications", "achievements"]
    resume_lower = resume.lower()
    found = [s for s in sections if s in resume_lower]
    score = min(len(found) * 14.3, 100)
    return round(score, 2), found


# ================================================================
#  6. GEMINI ANALYSIS (SAFE)
# ================================================================
GEMINI_PROMPT = """
You are an expert ATS (Applicant Tracking System) and career coach.
Analyze the resume against the job description below.

Return ONLY a valid JSON object:
{
  "semantic_score": <0-100>,
  "strengths": [],
  "improvements": [],
  "missing_skills": [],
  "overall_verdict": ""
}

--- JOB DESCRIPTION ---
{job_desc}

--- RESUME ---
{resume}
"""

def gemini_analysis(resume: str, job_desc: str) -> dict:
    default = {
        "semantic_score": 0,
        "strengths": [],
        "improvements": ["AI feedback unavailable (quota/API issue)"],
        "missing_skills": [],
        "overall_verdict": "AI analysis not available."
    }

    if not client:
        return default

    try:
        prompt = GEMINI_PROMPT.format(
            job_desc=job_desc[:2000],
            resume=resume[:4000]
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)

        result["semantic_score"] = max(0, min(int(result.get("semantic_score", 0)), 100))
        return result

    except Exception as e:
        print("Gemini error:", e)
        return default


# ================================================================
#  7. FINAL ATS CALCULATION
# ================================================================
def calculate_ats(resume: str, job_desc: str, use_ai=True):
    resume_clean = clean_text(resume)
    job_clean    = clean_text(job_desc)

    tfidf = tfidf_score(resume_clean, job_clean)
    kw_score, matched, missing = dynamic_keyword_score(resume, job_desc)
    sec_score, sections = section_score(resume)

    gemini_result = gemini_analysis(resume, job_desc) if use_ai else {}

    ai_score = gemini_result.get("semantic_score", 0)

    if use_ai and ai_score > 0:
        final = 0.4*ai_score + 0.3*kw_score + 0.2*tfidf + 0.1*sec_score
    else:
        final = 0.45*kw_score + 0.35*tfidf + 0.2*sec_score

    return {
        "ATS Score": round(final, 1),
        "AI Score": ai_score if ai_score > 0 else "Not Available",
        "Matched Skills": matched,
        "Missing Keywords": missing,
        "Suggestions": gemini_result.get("improvements", []),
        "AI Improvements": gemini_result.get("improvements", []),
        "Breakdown": {
            "AI Semantic": ai_score,
            "TF-IDF": round(tfidf, 1),
            "Keywords": round(kw_score, 1),
            "Sections": round(sec_score, 1),
        }
    }


# ================================================================
#  8. MAIN API
# ================================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")
        job_desc = request.form.get("job_desc", "")

        if not file or not job_desc:
            return jsonify({"error": "Missing resume or job description"}), 400

        mode = request.form.get("mode", "ai")
        use_ai = (mode == "ai")

        resume_text = extract_text(file)

        if not resume_text.strip():
            return jsonify({"error": "Empty resume"}), 400

        result = calculate_ats(resume_text, job_desc, use_ai)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================================================
#  RUN
# ================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
