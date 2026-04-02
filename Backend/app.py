from flask import Flask, request, jsonify
from flask_cors import CORS
import re

# OLD ML
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NEW AI MODEL 🔥
from sentence_transformers import SentenceTransformer, util

# PDF READER
import fitz

# ---------------- APP ----------------
app = Flask(__name__)
CORS(app)

# LOAD AI MODEL (loads once)
model = SentenceTransformer('all-MiniLM-L6-v2')


# ---------------- PDF EXTRACT ----------------
def extract_text(file):
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    except:
        return file.read().decode(errors="ignore")


# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9+ ]', ' ', text)
    return text


# ---------------- KEYWORD MATCH ----------------
def keyword_score(resume, job_desc):
    skills = [
        "python", "c++", "java", "javascript", "html", "css",
        "sql", "dbms", "git", "github",
        "data structures", "algorithms", "oop",
        "machine learning", "deep learning", "api", "flask"
    ]

    resume = resume.lower()
    job_desc = job_desc.lower()

    match = 0
    total = 0

    for skill in skills:
        if skill in job_desc:
            total += 1
            if skill in resume:
                match += 1

    if total == 0:
        return 0

    return (match / total) * 100


# ---------------- SECTION SCORE ----------------
def section_score(resume):
    sections = ["education", "skills", "projects", "experience"]
    resume = resume.lower()

    score = 0
    for sec in sections:
        if sec in resume:
            score += 25

    return score


# ---------------- TF-IDF SCORE ----------------
def tfidf_score(resume, job_desc):
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume, job_desc])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100
    except:
        return 0


# ---------------- 🧠 AI SCORE ----------------
def ai_semantic_score(resume, job_desc):
    try:
        emb1 = model.encode(resume, convert_to_tensor=True)
        emb2 = model.encode(job_desc, convert_to_tensor=True)

        score = util.cos_sim(emb1, emb2).item()
        return max(0, min(score * 100, 100))
    except:
        return 0


# ---------------- 🤖 AI IMPROVEMENTS ----------------
def ai_resume_improver(resume, job_desc):
    try:
        improvements = []

        if "project" not in resume.lower():
            improvements.append("Add 1-2 strong projects related to the job")

        if "experience" not in resume.lower():
            improvements.append("Add internships or real-world experience")

        if len(resume.split()) < 300:
            improvements.append("Expand resume with achievements and metrics")

        if "github" not in resume.lower():
            improvements.append("Include GitHub or portfolio links")

        improvements.append("Use strong action verbs (built, designed, optimized)")

        return improvements[:5]

    except:
        return ["Could not generate improvements"]


# ---------------- MISSING KEYWORDS ----------------
def get_missing_keywords(resume, job_desc):
    resume = clean_text(resume)
    job_desc = clean_text(job_desc)

    resume_words = set(resume.split())
    job_words = set(job_desc.split())

    stopwords = {
        "the","and","or","for","with","a","an","to","in","on","of","is","are"
    }

    job_words = job_words - stopwords
    missing = job_words - resume_words

    return list(missing)[:10]


# ---------------- MATCHED SKILLS ----------------
def skill_match(resume, job_desc):
    skills = [
        "python", "c++", "java", "javascript", "html", "css",
        "sql", "dbms", "git", "github",
        "data structures", "algorithms", "oop",
        "machine learning", "deep learning"
    ]

    resume = resume.lower()
    job_desc = job_desc.lower()

    return [s for s in skills if s in resume and s in job_desc]


# ---------------- SUGGESTIONS ----------------
def generate_suggestions(missing_keywords, ai_score, ats_score):
    suggestions = []

    for word in missing_keywords[:5]:
        suggestions.append(f"Add '{word}' to your resume")

    if ai_score < 60:
        suggestions.append("Improve resume alignment with job description")

    if ats_score < 50:
        suggestions.append("Your resume is weak — consider restructuring")

    if ats_score > 80:
        suggestions.append("Excellent resume for this job role!")

    return suggestions


# ---------------- FINAL ATS ----------------
def calculate_ats(resume, job_desc, use_ai=True):

    resume_clean = clean_text(resume)
    job_clean = clean_text(job_desc)

    # OLD SCORES
    tfidf = tfidf_score(resume_clean, job_clean)
    kw = keyword_score(resume_clean, job_clean)
    section = section_score(resume_clean)

    # AI SCORE
    ai_score = 0
    if use_ai:
        try:
            ai_score = ai_semantic_score(resume, job_desc)
        except:
            ai_score = 0

    # FINAL SCORE
    final_score = (
        (0.35 * ai_score if use_ai else 0) +
        0.30 * kw +
        0.20 * tfidf +
        0.15 * section
    )

    return round(final_score, 2), tfidf, kw, section, ai_score


# ---------------- API ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files["resume"]
        job_desc = request.form["job_desc"]

        # MODE (FAST / AI)
        mode = request.form.get("mode", "fast")
        use_ai = True if mode == "ai" else False

        print(f"⚡ Mode: {mode}")

        resume_text = extract_text(file)

        score, tfidf, kw, section, ai_score = calculate_ats(
            resume_text, job_desc, use_ai
        )

        missing = get_missing_keywords(resume_text, job_desc)
        matched = skill_match(resume_text, job_desc)
        suggestions = generate_suggestions(missing, ai_score, score)
        improvements = ai_resume_improver(resume_text, job_desc)

        return jsonify({
            "ATS Score": score,
            "AI Score": round(ai_score, 2),
            "Mode": mode,
            "Matched Skills": matched,
            "Missing Keywords": missing,
            "Suggestions": suggestions,
            "AI Improvements": improvements,
            "Breakdown": {
                "AI": round(ai_score, 2),
                "TF-IDF": round(tfidf, 2),
                "Keywords": round(kw, 2),
                "Sections": section
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)