import os
import re
import json

from flask import Flask, request, jsonify
from flask_cors import CORS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import fitz  # PyMuPDF

import google.generativeai as genai

# ---------------- APP SETUP ----------------
app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ================================================================
#  1. PDF TEXT EXTRACTION
# ================================================================
def extract_text(file) -> str:
    """Extract plain text from an uploaded PDF file."""
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
#  3. DYNAMIC KEYWORD EXTRACTION  (replaces hardcoded skill list)
#     Uses TF-IDF on the JD to find its most important terms,
#     then checks which ones appear in the resume.
# ================================================================
def dynamic_keyword_score(resume: str, job_desc: str):
    """
    Returns:
        score       - 0-100 based on % of JD keywords found in resume
        matched     - keywords found in both
        missing     - important JD keywords absent from resume
    """
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=500
        )
        vectorizer.fit([job_desc])

        feature_names = vectorizer.get_feature_names_out()
        jd_vector     = vectorizer.transform([job_desc]).toarray()[0]

        # Pick top-30 terms by TF-IDF weight in the JD
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
#  4. TF-IDF COSINE SIMILARITY  (baseline overlap score)
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
    """Returns score + list of detected sections."""
    sections = ["education", "skills", "projects", "experience",
                "summary", "certifications", "achievements"]
    resume_lower = resume.lower()
    found = [s for s in sections if s in resume_lower]
    score = min(len(found) * 14.3, 100)
    return round(score, 2), found


# ================================================================
#  6. GEMINI  -  SEMANTIC SCORE + DEEP FEEDBACK
# ================================================================
GEMINI_PROMPT = """
You are an expert ATS (Applicant Tracking System) and career coach.
Analyze the resume against the job description below.

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "semantic_score": <integer 0-100>,
  "strengths": [<up to 4 short strings>],
  "improvements": [<up to 5 specific, actionable strings>],
  "missing_skills": [<up to 8 skill/keyword strings specific to this JD>],
  "overall_verdict": "<one sentence summary>"
}}

--- JOB DESCRIPTION ---
{job_desc}

--- RESUME ---
{resume}
"""

def gemini_analysis(resume: str, job_desc: str) -> dict:
    """
    Calls Gemini Flash for semantic understanding.
    Returns a dict with score + structured feedback.
    Falls back gracefully if API key is missing or call fails.
    """
    default = {
        "semantic_score": 0,
        "strengths": [],
        "improvements": ["Set GEMINI_API_KEY environment variable for AI-powered feedback"],
        "missing_skills": [],
        "overall_verdict": "Gemini API not configured — showing TF-IDF score only."
    }

    if not GEMINI_API_KEY:
        return default

    try:
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")

        # Trim inputs to stay within token limits
        resume_trimmed = resume[:4000]
        jd_trimmed     = job_desc[:2000]

        prompt   = GEMINI_PROMPT.format(job_desc=jd_trimmed, resume=resume_trimmed)
        response = gemini_model.generate_content(prompt)

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$",     "", raw)

        result = json.loads(raw)

        for key in ("semantic_score", "strengths", "improvements",
                    "missing_skills", "overall_verdict"):
            if key not in result:
                return default

        result["semantic_score"] = max(0, min(int(result["semantic_score"]), 100))
        return result

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return default


# ================================================================
#  7. FINAL ATS SCORE  (weighted composite)
# ================================================================
#
#  Weight breakdown (with Gemini):
#    40%  Gemini semantic score  - actual meaning/context understanding
#    30%  Dynamic keyword match  - JD-specific keyword coverage
#    20%  TF-IDF cosine          - raw text overlap
#    10%  Section detection      - resume structure quality
#
#  Fallback (no Gemini):
#    45%  Dynamic keyword match
#    35%  TF-IDF cosine
#    20%  Section detection

def calculate_ats(resume: str, job_desc: str, use_ai: bool = True) -> dict:
    resume_clean = clean_text(resume)
    job_clean    = clean_text(job_desc)

    tfidf                            = tfidf_score(resume_clean, job_clean)
    kw_score, matched_kw, missing_kw = dynamic_keyword_score(resume, job_desc)
    sec_score, found_sections        = section_score(resume)

    gemini_result = {
        "semantic_score": 0,
        "strengths": [],
        "improvements": [],
        "missing_skills": [],
        "overall_verdict": ""
    }

    if use_ai:
        gemini_result = gemini_analysis(resume, job_desc)

    ai_score = gemini_result["semantic_score"]

    if use_ai and ai_score > 0:
        final = (
            0.40 * ai_score +
            0.30 * kw_score +
            0.20 * tfidf    +
            0.10 * sec_score
        )
    else:
        final = (
            0.45 * kw_score +
            0.35 * tfidf    +
            0.20 * sec_score
        )

    return {
        "ats_score":        round(final, 1),
        "ai_score":         ai_score,
        "tfidf_score":      round(tfidf, 1),
        "keyword_score":    round(kw_score, 1),
        "section_score":    round(sec_score, 1),
        "matched_keywords": matched_kw,
        "missing_keywords": missing_kw,
        "found_sections":   found_sections,
        "gemini":           gemini_result,
    }


# ================================================================
#  8. API ENDPOINT
# ================================================================
@app.route("/debug", methods=["GET"])
def debug():
    key = os.environ.get("GEMINI_API_KEY", "")
    return jsonify({
        "key_set": bool(key),
        "key_length": len(key),
        "key_preview": key[:8] if key else "EMPTY"
    })
```

**Step 4 — Commit it**
- Scroll down → click **"Commit changes"**
- Render will auto-detect the push and start redeploying

**Step 5 — Wait ~3-5 mins, then open this in your browser:**
```
https://resume-analyser-2gp6.onrender.com/debug
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file     = request.files.get("resume")
        job_desc = request.form.get("job_desc", "").strip()

        if not file or not job_desc:
            return jsonify({"error": "Both 'resume' (PDF) and 'job_desc' are required."}), 400

        mode   = request.form.get("mode", "ai")
        use_ai = (mode == "ai")

        print(f"[Request] mode={mode} | JD length={len(job_desc)}")

        resume_text = extract_text(file)

        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from the PDF."}), 400

        result = calculate_ats(resume_text, job_desc, use_ai)

        return jsonify({
            # Core scores
            "ATS Score":      result["ats_score"],
            "AI Score":       result["ai_score"],
            "Mode":           mode,

            # Keyword analysis (dynamic, JD-specific)
            "Matched Skills":   result["matched_keywords"],
            "Missing Keywords": result["missing_keywords"],

            # Resume structure
            "Found Sections":   result["found_sections"],

            # AI feedback from Gemini
            "Strengths":        result["gemini"]["strengths"],
            "Suggestions":      result["gemini"]["improvements"],
            "AI Improvements":  result["gemini"]["improvements"],
            "Overall Verdict":  result["gemini"]["overall_verdict"],
            "Gemini Missing":   result["gemini"]["missing_skills"],

            # Detailed breakdown
            "Breakdown": {
                "AI Semantic": result["ai_score"],
                "TF-IDF":      result["tfidf_score"],
                "Keywords":    result["keyword_score"],
                "Sections":    result["section_score"],
            }
        })

    except Exception as e:
        print(f"[Server Error] {e}")
        return jsonify({"error": str(e)}), 500


# ================================================================
#  9. RUN
# ================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
